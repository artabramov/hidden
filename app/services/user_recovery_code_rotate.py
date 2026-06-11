# app/services/user_recovery_code_rotate.py
# SPDX-License-Identifier: GPL-3.0-only

import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.audit import write_audit
from app.constants import OBSCURED_VALUE
from app.errors import ValueInvalidError
from app.events import Events as E
from app.hooks import hooks
from app.models.user import User
from app.repositories.orm import ORMRepository
from app.schemas.user_recovery_code_rotate import UserRecoveryCodeRotateRequest
from app.security.encryption import encrypt_string
from app.security.hashing import hash_string, is_password_correct
from app.security.jwt import generate_jti
from app.security.recovery import generate_recovery_code

log = logging.getLogger(__name__)


async def rotate_recovery_code(
    session: AsyncSession,
    user: User,
    data: UserRecoveryCodeRotateRequest,
) -> str:
    """
    Rotate the user's recovery code after validating the submitted
    recovery code against the stored hash, persist the new hash, reset
    failed recovery counters, rotate JTI, and return the plaintext
    recovery code for one-time client display.
    """
    log.info("event=%s user_id=%s", E.USER_RECOVERY_CODE_ROTATE_STARTED, user.id)  # noqa: E501

    if not is_password_correct(
        data.recovery_code,
        user.recovery_code_hash,
    ):
        log.warning("event=%s", E.USER_RECOVERY_CODE_ROTATE_RECOVERY_CODE_INVALID)  # noqa: E501
        raise ValueInvalidError(
            field="recovery_code",
            input_value=OBSCURED_VALUE,
        )

    new_recovery_code = generate_recovery_code()
    user.recovery_code_hash = hash_string(new_recovery_code)
    user.failed_recovery_code_attempts = 0
    user.password_verified_at = None

    current_jti = generate_jti()
    user.current_jti_encrypted = encrypt_string(current_jti)

    repository = ORMRepository(session)
    await repository.update(user)

    await write_audit(
        repository=repository,
        event=E.USER_RECOVERY_CODE_ROTATE_COMPLETED,
        resource_type=User.__tablename__,
        resource_id=user.id,
    )
    await repository.commit()

    log.info("event=%s", E.USER_RECOVERY_CODE_ROTATE_COMPLETED)
    await hooks.emit(E.USER_RECOVERY_CODE_ROTATE_COMPLETED, session, user)
    return new_recovery_code
