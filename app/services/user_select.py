# app/services/user_select.py
# SPDX-License-Identifier: SSPL-1.0

import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.errors import (
    ResourceForbiddenError,
    ResourceNotFoundError,
)
from app.events import Events as E
from app.hooks import hooks
from app.models.user import User
from app.repositories.orm import ORMRepository

log = logging.getLogger(__name__)


async def select_user(
    session: AsyncSession,
    current_user: User,
    user_id: int,
) -> User:
    """
    Retrieve a user by identifier by enforcing access control, allowing
    self-access or admin access, and returning the selected user record.
    """
    log.info("event=%s user_id=%s", E.USER_SELECT_STARTED, user_id)

    repository = ORMRepository(session)
    user = await repository.select(User, obj_id=user_id)
    if user is None:
        log.warning("event=%s", E.USER_SELECT_USER_NOT_FOUND)
        raise ResourceNotFoundError

    if not current_user.can_admin and current_user.id != user_id:
        log.warning("event=%s", E.USER_SELECT_DENIED)
        raise ResourceForbiddenError

    log.info("event=%s", E.USER_SELECT_COMPLETED)
    await hooks.emit(E.USER_SELECT_COMPLETED, session, user)
    return user
