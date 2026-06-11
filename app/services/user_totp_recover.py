# app/services/user_totp_recover.py
# SPDX-License-Identifier: GPL-3.0-only

import logging
import time

from sqlalchemy.ext.asyncio import AsyncSession

from app.audit import write_audit
from app.constants import (
    AUTH_FAILED_RECOVERY_CODE_ATTEMPTS,
    AUTH_FAILED_SUSPEND_SECONDS,
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
from app.schemas.user_totp_recover import UserTotpRecoverRequest
from app.security.encryption import encrypt_string
from app.security.hashing import is_password_correct
from app.security.jwt import generate_jti
from app.security.totp import generate_totp_secret

log = logging.getLogger(__name__)


async def recover_totp(
    session: AsyncSession,
    data: UserTotpRecoverRequest,
) -> tuple[int, str]:
    """
    Verify MFA session and recovery code; on success rotate TOTP secret,
    rotate JTI (invalidating prior access tokens), clear MFA state, and
    return user_id and plaintext TOTP secret.
    """
    log.info("event=%s", E.USER_TOTP_RECOVER_STARTED)

    repository = ORMRepository(session)
    user = await repository.select(
        User,
        mfa_session_uuid=data.mfa_session_uuid,
    )

    if user is None:
        log.warning("event=%s", E.USER_TOTP_RECOVER_USER_NOT_FOUND)
        raise ValueAuthenticationError(
            field="recovery_code",
            input_value=data.recovery_code,
        )

    if not user.is_active:
        log.warning("event=%s user_id=%s", E.USER_TOTP_RECOVER_USER_INACTIVE, user.id)  # noqa: E501
        raise ValueAuthenticationError(
            field="recovery_code",
            input_value=data.recovery_code,
        )

    now = int(time.time())
    if user.suspended_until is not None and user.suspended_until > now:
        log.warning("event=%s user_id=%s", E.USER_TOTP_RECOVER_USER_SUSPENDED, user.id)  # noqa: E501
        raise ValueAuthenticationError(
            field="recovery_code",
            input_value=data.recovery_code,
        )

    if (
        user.password_verified_at is None or
        user.password_verified_at + AUTH_PASSWORD_VERIFIED_TTL_SECONDS < now
    ):
        user.mfa_session_uuid = None
        user.password_verified_at = None
        await repository.update(user)
        await repository.commit()

        log.warning("event=%s user_id=%s", E.USER_TOTP_RECOVER_PASSWORD_NOT_VERIFIED, user.id)  # noqa: E501
        raise ResourceConflictError

    if not is_password_correct(data.recovery_code, user.recovery_code_hash):

        user.failed_recovery_code_attempts += 1
        if user.failed_recovery_code_attempts >= (
            AUTH_FAILED_RECOVERY_CODE_ATTEMPTS
        ):
            user.failed_recovery_code_attempts = 0
            user.mfa_session_uuid = None
            user.password_verified_at = None
            user.suspended_until = now + AUTH_FAILED_SUSPEND_SECONDS

        await repository.update(user)
        await repository.commit()

        log.warning("event=%s user_id=%s", E.USER_TOTP_RECOVER_RECOVERY_CODE_INVALID, user.id)  # noqa: E501
        raise ValueAuthenticationError(
            field="recovery_code",
            input_value=data.recovery_code,
        )

    totp_secret = generate_totp_secret()
    current_jti = generate_jti()

    user.totp_secret_encrypted = encrypt_string(totp_secret)
    user.current_jti_encrypted = encrypt_string(current_jti)
    user.mfa_session_uuid = None
    user.password_verified_at = None
    user.failed_recovery_code_attempts = 0
    user.failed_totp_attempts = 0

    await repository.update(user)

    await write_audit(
        repository=repository,
        current_user_id=user.id,
        event=E.USER_TOTP_RECOVER_COMPLETED,
        resource_type=User.__tablename__,
        resource_id=user.id,
    )
    await repository.commit()

    log.info("event=%s user_id=%s", E.USER_TOTP_RECOVER_COMPLETED, user.id)
    await hooks.emit(E.USER_TOTP_RECOVER_COMPLETED, session, user)
    return user.id, totp_secret
