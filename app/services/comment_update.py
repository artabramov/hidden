# app/services/comment_update.py
# SPDX-License-Identifier: GPL-3.0-only

import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.audit import write_audit
from app.errors import (
    ResourceForbiddenError,
    ResourceLockedError,
    ResourceNotFoundError,
)
from app.events import Events as E
from app.hooks import hooks
from app.models.file_comment import FileComment
from app.models.user import User
from app.repositories.orm import ORMRepository
from app.schemas.comment_update import CommentUpdateRequest

log = logging.getLogger(__name__)


async def update_comment(
    session: AsyncSession,
    user: User,
    comment_id: int,
    data: CommentUpdateRequest,
) -> FileComment:
    """
    Update an existing file comment. Only the comment creator may
    update it, and the parent folder must not be write-protected.
    """
    log.info("event=%s comment_id=%s", E.COMMENT_UPDATE_STARTED, comment_id)

    repository = ORMRepository(session)
    comment = await repository.select(FileComment, obj_id=comment_id)

    if comment is None:
        log.warning("event=%s", E.COMMENT_UPDATE_COMMENT_NOT_FOUND)
        raise ResourceNotFoundError

    if comment.created_by != user.id:
        log.warning("event=%s", E.COMMENT_UPDATE_FORBIDDEN)
        raise ResourceForbiddenError

    folder = comment.comment_file.file_folder
    parent_chain = await repository.select_parent_chain(folder)

    if (
        folder.is_write_protected or
        folder.is_write_protected_recursive(parent_chain)
    ):
        log.warning("event=%s", E.COMMENT_UPDATE_PARENT_WRITE_PROTECTED)
        raise ResourceLockedError

    comment.body = data.body
    await repository.update(comment)

    await write_audit(
        repository=repository,
        event=E.COMMENT_UPDATE_COMPLETED,
        resource_type=FileComment.__tablename__,
        resource_id=comment.id,
    )
    await repository.commit()

    log.info("event=%s", E.COMMENT_UPDATE_COMPLETED)
    await hooks.emit(E.COMMENT_UPDATE_COMPLETED, session, comment)

    return comment
