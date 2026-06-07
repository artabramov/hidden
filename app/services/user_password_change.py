# app/services/user_password_change.py
# SPDX-License-Identifier: SSPL-1.0

import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.audit import write_audit
from app.constants import OBSCURED_VALUE
from app.errors import ValueInvalidError
from app.events import Events as E
from app.hooks import hooks
from app.models.user import User
from app.repositories.orm import ORMRepository
from app.schemas.user_password_change import UserPasswordChangeRequest
from app.security.encryption import encrypt_string
from app.security.hashing import hash_string, is_password_correct
from app.security.jwt import generate_jti

log = logging.getLogger(__name__)


# NOTE (ADR-40): Updating password to the same value is allowed.
# Updating to the current password is permitted and treated as a no-op.
# This avoids requiring a second update to restore original credentials,
# which is needed for E2E/behave scenarios that reuse baseline users.

# NOTE (ADR-41): Password change invalidates all tokens.
# It resets verification state and rotates JTI, invalidating all
# existing JWT tokens.

async def change_password(
    session: AsyncSession,
    user: User,
    data: UserPasswordChangeRequest,
) -> None:
    """
    Change the current user's password by validating the current
    password against the stored hash, updating the password hash,
    and persisting the modified user record.
    """
    log.info("event=%s user_id=%s", E.USER_PASSWORD_CHANGE_STARTED, user.id)

    if not is_password_correct(
        data.current_password,
        user.password_hash,
    ):
        log.warning("event=%s", E.USER_PASSWORD_CHANGE_PASSWORD_INVALID)
        raise ValueInvalidError(
            field="current_password",
            input_value=OBSCURED_VALUE,
        )

    user.password_hash = hash_string(data.changed_password)
    user.password_verified_at = None

    current_jti = generate_jti()
    user.current_jti_encrypted = encrypt_string(current_jti)

    repository = ORMRepository(session)
    await repository.update(user)

    await write_audit(
        repository=repository,
        event=E.USER_PASSWORD_CHANGE_COMPLETED,
        resource_type=User.__tablename__,
        resource_id=user.id,
    )
    await repository.commit()

    log.info("event=%s", E.USER_PASSWORD_CHANGE_COMPLETED)
    await hooks.emit(E.USER_PASSWORD_CHANGE_COMPLETED, session, user)
