# app/services/user_login.py
# SPDX-License-Identifier: SSPL-1.0

import logging
import time

from sqlalchemy.ext.asyncio import AsyncSession

from app.audit import write_audit
from app.constants import (
    AUTH_FAILED_PASSWORD_ATTEMPTS,
    AUTH_FAILED_SUSPEND_SECONDS,
)
from app.errors import ValueAuthenticationError
from app.events import Events as E
from app.hooks import hooks
from app.models.user import User
from app.repositories.orm import ORMRepository
from app.schemas.user_login import UserLoginRequest
from app.security.hashing import is_password_correct
from app.security.totp import generate_mfa_session_uuid

log = logging.getLogger(__name__)


# NOTE (ADR-38): Timing-based username enumeration is not mitigated.
# In a self-hosted model, reliable timing analysis implies access to a
# trusted environment and indicates a broader security breach. This risk
# is accepted and not explicitly mitigated in the authentication flow.

async def login_user(
    session: AsyncSession,
    data: UserLoginRequest,
) -> str:
    """
    Authenticate a user by validating the provided password, checking
    account status, updating authentication flags and failed attempt
    counters, issuing a temporary MFA session UUID on success, and
    applying temporary suspension on repeated authentication failures.
    """
    log.info("event=%s", E.USER_LOGIN_STARTED)

    repository = ORMRepository(session)
    user = await repository.select(User, username=data.username)
    if user is None:

        # TODO: Optional defense-in-depth. Consider normalizing timing
        # between "user not found" and "invalid password" (e.g., dummy
        # password hash verification for non-existent users). This is
        # not required under the current threat model.

        log.warning("event=%s", E.USER_LOGIN_USERNAME_NOT_FOUND)
        raise ValueAuthenticationError(
            field="username",
            input_value=data.username,
        )

    if not user.is_active:
        log.warning("event=%s user_id=%s", E.USER_LOGIN_USER_INACTIVE, user.id)
        raise ValueAuthenticationError(
            field="username",
            input_value=data.username,
        )

    now = int(time.time())
    if user.suspended_until is not None and user.suspended_until > now:
        log.warning("event=%s user_id=%s", E.USER_LOGIN_USER_SUSPENDED, user.id)  # noqa: E501
        raise ValueAuthenticationError(
            field="username",
            input_value=data.username,
        )

    if is_password_correct(data.password, user.password_hash):
        mfa_session_uuid = generate_mfa_session_uuid()

        user.failed_password_attempts = 0
        user.password_verified_at = now
        user.suspended_until = None
        user.mfa_session_uuid = mfa_session_uuid
        await repository.update(user)

        await write_audit(
            repository=repository,
            current_user_id=user.id,
            event=E.USER_LOGIN_COMPLETED,
            resource_type=User.__tablename__,
            resource_id=user.id,
        )
        await repository.commit()

        log.info("event=%s user_id=%s", E.USER_LOGIN_COMPLETED, user.id)
        await hooks.emit(E.USER_LOGIN_COMPLETED, session, user)

        return mfa_session_uuid

    else:
        # Do not reset mfa_session_uuid here; it is invalidated
        # only during the MFA step to avoid breaking an in-progress
        # second-factor session.

        user.failed_password_attempts += 1
        user.password_verified_at = None

        if user.failed_password_attempts >= AUTH_FAILED_PASSWORD_ATTEMPTS:
            user.failed_password_attempts = 0
            user.suspended_until = now + AUTH_FAILED_SUSPEND_SECONDS

        await repository.update(user)
        await repository.commit()

        log.warning("event=%s user_id=%s", E.USER_LOGIN_PASSWORD_INVALID, user.id)  # noqa: E501
        raise ValueAuthenticationError(
            field="username",
            input_value=data.username,
        )
