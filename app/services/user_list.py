# app/services/user_list.py
# SPDX-License-Identifier: GPL-3.0-only

import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.events import Events as E
from app.hooks import hooks
from app.models.user import User
from app.repositories.orm import ORMRepository
from app.schemas.user_list import UserListRequest

log = logging.getLogger(__name__)


async def list_users(
    session: AsyncSession,
    params: UserListRequest,
) -> tuple[list[User], int]:
    """
    List users by applying filtering, pagination, and ordering
    parameters and returning matching user records along with the
    total count.
    """
    log.info("event=%s", E.USER_LIST_STARTED)

    repository = ORMRepository(session)
    filters = params.model_dump(exclude_none=True)

    if "username__ilike" in filters:
        filters["username__ilike"] = f"%{filters['username__ilike']}%"

    if "display_name__ilike" in filters:
        filters["display_name__ilike"] = (
            f"%{filters['display_name__ilike']}%"
        )

    users_count = await repository.count_all(User, **filters)
    users = await repository.select_all(User, **filters)

    log.info("event=%s", E.USER_LIST_COMPLETED)
    await hooks.emit(E.USER_LIST_COMPLETED, session, users)
    return users, users_count
