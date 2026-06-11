# app/services/comment_delete.py
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
from app.locks import LockType, locks
from app.models.file_comment import FileComment
from app.models.user import User
from app.repositories.orm import ORMRepository

log = logging.getLogger(__name__)


async def delete_comment(
    session: AsyncSession,
    user: User,
    comment_id: int,
) -> FileComment:
    """
    Delete an existing file comment. Only the comment creator may
    delete it, and the parent folder must not be write-protected.
    """
    log.info("event=%s comment_id=%s", E.COMMENT_DELETE_STARTED, comment_id)

    repository = ORMRepository(session)
    comment = await repository.select(FileComment, obj_id=comment_id)

    if comment is None:
        log.warning("event=%s", E.COMMENT_DELETE_COMMENT_NOT_FOUND)
        raise ResourceNotFoundError

    if comment.created_by != user.id:
        log.warning("event=%s", E.COMMENT_DELETE_FORBIDDEN)
        raise ResourceForbiddenError

    folder = comment.comment_file.file_folder
    parent_chain = await repository.select_parent_chain(folder)

    if (
        folder.is_write_protected or
        folder.is_write_protected_recursive(parent_chain)
    ):
        log.warning("event=%s", E.COMMENT_DELETE_PARENT_WRITE_PROTECTED)
        raise ResourceLockedError

    file_path = comment.comment_file.get_absolute_path(folder, parent_chain)
    async with locks.lock_file(file_path, LockType.WRITE):
        await repository.delete(comment)

        comment.comment_file.comments_count -= 1
        await repository.update(comment.comment_file)

        await write_audit(
            repository=repository,
            event=E.COMMENT_DELETE_COMPLETED,
            resource_type=FileComment.__tablename__,
            resource_id=comment.id,
        )
        await repository.commit()

    log.info("event=%s", E.COMMENT_DELETE_COMPLETED)
    await hooks.emit(E.COMMENT_DELETE_COMPLETED, session, comment)

    return comment
