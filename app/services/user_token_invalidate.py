# app/services/user_token_invalidate.py
# SPDX-License-Identifier: GPL-3.0-only

import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.audit import write_audit
from app.events import Events as E
from app.hooks import hooks
from app.models.user import User
from app.repositories.orm import ORMRepository
from app.security.encryption import encrypt_string
from app.security.jwt import generate_jti

log = logging.getLogger(__name__)


async def invalidate_token(
    session: AsyncSession,
    user: User,
) -> None:
    """
    Invalidate the current authentication token by generating a new
    token identifier (JTI), updating the stored encrypted JTI, and
    persisting the modified user record.
    """
    log.info("event=%s user_id=%s", E.USER_TOKEN_INVALIDATE_STARTED, user.id)

    current_jti = generate_jti()
    user.current_jti_encrypted = encrypt_string(current_jti)

    repository = ORMRepository(session)
    await repository.update(user)

    await write_audit(
        repository=repository,
        event=E.USER_TOKEN_INVALIDATE_COMPLETED,
        resource_type=User.__tablename__,
        resource_id=user.id,
    )
    await repository.commit()

    log.info("event=%s", E.USER_TOKEN_INVALIDATE_COMPLETED)
    await hooks.emit(E.USER_TOKEN_INVALIDATE_COMPLETED, session, user)
