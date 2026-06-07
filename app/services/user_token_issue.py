# app/services/user_token_issue.py
# SPDX-License-Identifier: SSPL-1.0

import logging
import time

from sqlalchemy.ext.asyncio import AsyncSession

from app.audit import write_audit
from app.config import get_config
from app.constants import (
    AUTH_FAILED_SUSPEND_SECONDS,
    AUTH_FAILED_TOTP_ATTEMPTS,
    AUTH_PASSWORD_VERIFIED_TTL_SECONDS,
)
from app.errors import (
    ResourceConflictError,
    ValueAuthenticationError,
)
from app.events import Events as E
from app.hooks import hooks
from app.models.user import User
from app.repositories.orm import ORMRepository
from app.schemas.user_token_issue import TokenIssueRequest
from app.security.encryption import decrypt_string, encrypt_string
from app.security.jwt import create_auth_token, generate_jti
from app.security.totp import is_totp_correct

log = logging.getLogger(__name__)


# NOTE (ADR-37): Authentication is implemented as a two-step flow.
# The steps are linked by a short-lived MFA session UUID and password
# verification timestamp. The session UUID is invalidated during token
# issuance to prevent reuse of the second authentication step.

async def issue_token(
    session: AsyncSession,
    data: TokenIssueRequest,
) -> tuple[int, str]:
    """
    Issue an authentication token by verifying the provided TOTP code,
    enforcing account state and password verification, generating a new
    token identifier (JTI), updating authentication state and failure
    counters, and applying suspension on repeated TOTP failures.
    """
    log.info("event=%s", E.USER_TOKEN_ISSUE_STARTED)

    repository = ORMRepository(session)
    user = await repository.select(
        User,
        mfa_session_uuid=data.mfa_session_uuid,
    )

    if user is None:
        log.warning("event=%s", E.USER_TOKEN_ISSUE_USER_NOT_FOUND)
        raise ValueAuthenticationError(
            field="totp",
            input_value=data.totp,
        )

    if not user.is_active:
        log.warning("event=%s user_id=%s", E.USER_TOKEN_ISSUE_USER_INACTIVE, user.id)  # noqa: E501
        raise ValueAuthenticationError(
            field="totp",
            input_value=data.totp,
        )

    now = int(time.time())
    if user.suspended_until is not None and user.suspended_until > now:
        log.warning("event=%s user_id=%s", E.USER_TOKEN_ISSUE_USER_SUSPENDED, user.id)  # noqa: E501
        raise ValueAuthenticationError(
            field="totp",
            input_value=data.totp,
        )

    if (
        user.password_verified_at is None or
        user.password_verified_at + AUTH_PASSWORD_VERIFIED_TTL_SECONDS < now
    ):
        user.mfa_session_uuid = None
        user.password_verified_at = None
        await repository.update(user)
        await repository.commit()

        log.warning("event=%s user_id=%s", E.USER_TOKEN_ISSUE_PASSWORD_NOT_VERIFIED, user.id)  # noqa: E501
        raise ResourceConflictError

    totp_secret = decrypt_string(user.totp_secret_encrypted)
    if not is_totp_correct(totp_secret, data.totp):

        # TODO: Optional defense-in-depth. Consider normalizing timing
        # between early rejection paths and TOTP verification (e.g.,
        # dummy TOTP verification or equivalent constant-time operation
        # for non-existent users). This is not required under the
        # current threat model.

        user.failed_totp_attempts += 1
        if user.failed_totp_attempts >= AUTH_FAILED_TOTP_ATTEMPTS:
            user.failed_totp_attempts = 0
            user.mfa_session_uuid = None
            user.password_verified_at = None
            user.suspended_until = now + AUTH_FAILED_SUSPEND_SECONDS

        await repository.update(user)
        await repository.commit()

        log.warning("event=%s user_id=%s", E.USER_TOKEN_ISSUE_TOTP_INVALID, user.id)  # noqa: E501
        raise ValueAuthenticationError(
            field="totp",
            input_value=data.totp,
        )

    current_jti = generate_jti()
    disable_exp = data.disable_exp and get_config().AUTH_ALLOW_PERMANENT_TOKENS
    auth_token = create_auth_token(
        user.id,
        current_jti,
        disable_exp=disable_exp,
    )

    user.last_authenticated_at = now
    user.current_jti_encrypted = encrypt_string(current_jti)
    user.password_verified_at = None
    user.failed_totp_attempts = 0
    user.mfa_session_uuid = None
    await repository.update(user)

    await write_audit(
        repository=repository,
        current_user_id=user.id,
        event=E.USER_TOKEN_ISSUE_COMPLETED,
        resource_type=User.__tablename__,
        resource_id=user.id,
    )
    await repository.commit()

    log.info("event=%s user_id=%s", E.USER_TOKEN_ISSUE_COMPLETED, user.id)
    await hooks.emit(E.USER_TOKEN_ISSUE_COMPLETED, session, user)
    return user.id, auth_token
