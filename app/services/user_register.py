# app/services/user_register.py
# SPDX-License-Identifier: GPL-3.0-only

import logging
import time

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.audit import write_audit
from app.config import get_config
from app.constants import (
    AUTH_FIRST_ADMIN_LOCK_FLAG_PATH,
    REGISTER_ATTEMPTS_LIMIT,
    REGISTER_ATTEMPTS_WINDOW_SECONDS,
)
from app.errors import (
    TooManyRequestsError,
    ValueConflictError,
)
from app.events import Events as E
from app.hooks import hooks
from app.locks import LockType, locks
from app.models.user import User, UserRole
from app.repositories.file import touch
from app.repositories.orm import ORMRepository
from app.schemas.user_register import UserRegisterRequest
from app.security.encryption import encrypt_string
from app.security.hashing import hash_string
from app.security.recovery import generate_recovery_code
from app.security.totp import generate_totp_secret

log = logging.getLogger(__name__)


# NOTE (ADR-35): The "first user becomes admin" flow is serialized.
# An application-level lock ensures only one initial admin assignment.
# After the initial admin is committed, a flag file is created under
# the secrets volume so health check can report bootstrap progress
# without cipherdir mount.

# NOTE (ADR-36): Registration throttling limits successful creations.
# It is based on the number of recently created users (created_at)
# within a time window. Attempts with existing usernames are rejected
# earlier and do not count toward the throttle, as they never enter
# the critical section.


async def register_user(
    session: AsyncSession,
    data: UserRegisterRequest,
) -> tuple[User, str, str]:
    """
    Register a new user by validating username uniqueness, enforcing a
    registration rate limit, generating a TOTP secret and recovery code,
    assigning initial role and activation status (first user becomes
    admin), persisting the user record, and returning the created user
    with the TOTP secret and plaintext recovery code (same primitive as
    password for the stored recovery hash).
    """
    log.info("event=%s", E.USER_REGISTER_STARTED)

    repository = ORMRepository(session)
    existing_user = await repository.select(
        User,
        username=data.username,
    )

    if existing_user is not None:
        log.warning("event=%s", E.USER_REGISTER_USERNAME_EXISTS)
        raise ValueConflictError(
            field="username",
            input_value=data.username,
        )

    totp_secret = generate_totp_secret()
    recovery_code = generate_recovery_code()

    async with locks.lock_file(
        AUTH_FIRST_ADMIN_LOCK_FLAG_PATH,
        LockType.WRITE,
    ):
        attempts_time = int(time.time()) - REGISTER_ATTEMPTS_WINDOW_SECONDS
        recent_users_count = await repository.count_all(
            User,
            created_at__gt=attempts_time,
        )
        if recent_users_count >= REGISTER_ATTEMPTS_LIMIT:
            log.warning("event=%s", E.USER_REGISTER_ATTEMPTS_LIMITED)
            raise TooManyRequestsError

        is_active = False
        role = UserRole.READER.value

        users_count = await repository.count_all(User)
        is_first_admin = users_count == 0
        if is_first_admin:
            is_active = True
            role = UserRole.ADMIN.value

        user = User(
            is_active=is_active,
            role=role,
            username=data.username,
            password_hash=hash_string(data.password),
            display_name=data.display_name,
            summary=data.summary,
            totp_secret_encrypted=encrypt_string(totp_secret),
            recovery_code_hash=hash_string(recovery_code),
        )

        try:
            await repository.insert(user)
        except IntegrityError:
            await repository.rollback()
            log.warning("event=%s", E.USER_REGISTER_USERNAME_EXISTS)
            raise ValueConflictError(
                field="username",
                input_value=data.username,
            )

    await write_audit(
        repository=repository,
        current_user_id=user.id,
        event=E.USER_REGISTER_COMPLETED,
        resource_type=User.__tablename__,
        resource_id=user.id,
    )
    await repository.commit()

    if is_first_admin:
        config = get_config()
        await touch(config.FIRST_ADMIN_CREATED_FLAG_PATH)

    log.info("event=%s user_id=%s", E.USER_REGISTER_COMPLETED, user.id)
    await hooks.emit(E.USER_REGISTER_COMPLETED, session, user)
    return user, totp_secret, recovery_code
