# app/services/user_role_change.py
# SPDX-License-Identifier: GPL-3.0-only

import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.audit import write_audit
from app.errors import ResourceForbiddenError, ResourceNotFoundError
from app.events import Events as E
from app.hooks import hooks
from app.models.user import User
from app.repositories.orm import ORMRepository
from app.schemas.user_role_change import UserRoleChangeRequest

log = logging.getLogger(__name__)


# NOTE (ADR-39): Admins manage roles with self-update protection.
# Admins may update role and active flag for other users, including
# granting or revoking admin rights. Self-update is restricted to
# prevent accidental self-demotion or lockout.

async def change_user_role(
    session: AsyncSession,
    current_user: User,
    user_id: int,
    data: UserRoleChangeRequest,
) -> None:
    """
    Change a user's role and activation status by preventing
    self-update, retrieving the target user, applying role and
    status updates, and persisting the modified user record.
    """
    log.info("event=%s user_id=%s", E.USER_ROLE_CHANGE_STARTED, user_id)

    if current_user.id == user_id:
        log.warning("event=%s", E.USER_ROLE_CHANGE_DENIED)
        raise ResourceForbiddenError

    repository = ORMRepository(session)
    user = await repository.select(User, obj_id=user_id)
    if user is None:
        log.warning("event=%s", E.USER_ROLE_CHANGE_USER_NOT_FOUND)
        raise ResourceNotFoundError

    user.role = data.role.value
    user.is_active = data.is_active
    await repository.update(user)

    await write_audit(
        repository=repository,
        event=E.USER_ROLE_CHANGE_COMPLETED,
        resource_type=User.__tablename__,
        resource_id=user.id,
    )
    await repository.commit()

    log.info("event=%s", E.USER_ROLE_CHANGE_COMPLETED)
    await hooks.emit(E.USER_ROLE_CHANGE_COMPLETED, session, user)
