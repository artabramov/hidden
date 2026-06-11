# app/services/comment_create.py
# SPDX-License-Identifier: GPL-3.0-only

import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.audit import write_audit
from app.errors import ResourceLockedError, ResourceNotFoundError
from app.events import Events as E
from app.hooks import hooks
from app.locks import LockType, locks
from app.models.file import File
from app.models.file_comment import FileComment
from app.models.user import User
from app.repositories.orm import ORMRepository
from app.schemas.comment_create import CommentCreateRequest

log = logging.getLogger(__name__)


async def create_comment(
    session: AsyncSession,
    user: User,
    file_id: int,
    data: CommentCreateRequest,
) -> FileComment:
    """
    Create a comment for an existing file. The target file must exist,
    and its parent folder must not be write-protected recursively.
    """
    log.info("event=%s file_id=%s", E.COMMENT_CREATE_STARTED, file_id)

    repository = ORMRepository(session)
    file = await repository.select(File, obj_id=file_id)

    if file is None:
        log.warning("event=%s", E.COMMENT_CREATE_FILE_NOT_FOUND)
        raise ResourceNotFoundError

    parent_chain = await repository.select_parent_chain(file.file_folder)

    if (
        file.file_folder.is_write_protected or
        file.file_folder.is_write_protected_recursive(parent_chain)
    ):
        log.warning("event=%s", E.COMMENT_CREATE_PARENT_WRITE_PROTECTED)
        raise ResourceLockedError

    file_path = file.get_absolute_path(file.file_folder, parent_chain)
    async with locks.lock_file(file_path, LockType.WRITE):
        comment = FileComment(
            file_id=file.id,
            created_by=user.id,
            body=data.body,
        )
        await repository.insert(comment)

        file.comments_count += 1
        await repository.update(file)

        await write_audit(
            repository=repository,
            event=E.COMMENT_CREATE_COMPLETED,
            resource_type=FileComment.__tablename__,
            resource_id=comment.id,
        )
        await repository.commit()

    log.info("event=%s comment_id=%s", E.COMMENT_CREATE_COMPLETED, comment.id)
    await hooks.emit(E.COMMENT_CREATE_COMPLETED, session, comment)

    return comment
