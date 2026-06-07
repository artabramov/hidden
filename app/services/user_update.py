# app/services/user_update.py
# SPDX-License-Identifier: SSPL-1.0

import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.audit import write_audit
from app.events import Events as E
from app.hooks import hooks
from app.models.user import User
from app.repositories.orm import ORMRepository
from app.schemas.user_update import UserUpdateRequest

log = logging.getLogger(__name__)


async def update_user(
    session: AsyncSession,
    user: User,
    data: UserUpdateRequest,
) -> None:
    """
    Update the user's profile by applying provided field changes,
    including conditional summary update, and persisting the modified
    user record.
    """
    log.info("event=%s user_id=%s", E.USER_UPDATE_STARTED, user.id)

    user.display_name = data.display_name
    if "summary" in data.model_fields_set:
        user.summary = data.summary

    repository = ORMRepository(session)
    await repository.update(user)

    await write_audit(
        repository=repository,
        event=E.USER_UPDATE_COMPLETED,
        resource_type=User.__tablename__,
        resource_id=user.id,
    )
    await repository.commit()

    log.info("event=%s", E.USER_UPDATE_COMPLETED)
    await hooks.emit(E.USER_UPDATE_COMPLETED, session, user)
