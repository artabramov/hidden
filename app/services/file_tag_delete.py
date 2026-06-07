# app/services/file_tag_delete.py
# SPDX-License-Identifier: SSPL-1.0

import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.audit import write_audit
from app.errors import ResourceLockedError, ResourceNotFoundError
from app.events import Events as E
from app.hooks import hooks
from app.models.file import File
from app.models.file_tag import FileTag
from app.repositories.orm import ORMRepository
from app.schemas.file_tag_path import FileTagPath

log = logging.getLogger(__name__)


async def delete_file_tag(
    session: AsyncSession,
    path: FileTagPath,
) -> None:
    """
    Delete a tag from an existing file. The operation is idempotent:
    if the file does not have the tag, no row is deleted.
    """
    log.info("event=%s file_id=%s", E.TAG_DELETE_STARTED, path.file_id)

    repository = ORMRepository(session)
    file = await repository.select(File, obj_id=path.file_id)

    if file is None:
        log.warning("event=%s", E.TAG_DELETE_FILE_NOT_FOUND)
        raise ResourceNotFoundError

    parent_chain = await repository.select_parent_chain(file.file_folder)

    if (
        file.file_folder.is_write_protected or
        file.file_folder.is_write_protected_recursive(parent_chain)
    ):
        log.warning("event=%s", E.TAG_DELETE_PARENT_WRITE_PROTECTED)
        raise ResourceLockedError

    tag = await repository.select(
        FileTag,
        file_id=file.id,
        tag=path.tag,
    )

    if tag is None:
        return

    await repository.delete(tag)

    await write_audit(
        repository=repository,
        event=E.TAG_DELETE_COMPLETED,
        resource_type=FileTag.__tablename__,
        resource_id=tag.id,
    )
    await repository.commit()

    log.info("event=%s tag_id=%s", E.TAG_DELETE_COMPLETED, tag.id)
    await hooks.emit(E.TAG_DELETE_COMPLETED, session, tag)
