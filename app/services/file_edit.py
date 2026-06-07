# app/services/file_edit.py
# SPDX-License-Identifier: SSPL-1.0

import asyncio
import logging
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.audit import write_audit
from app.errors import (
    ResourceConflictError,
    ResourceLockedError,
    ResourceNotFoundError,
)
from app.events import Events as E
from app.hooks import hooks
from app.locks import LockType, locks
from app.models.file import File
from app.models.file_revision import FileRevision
from app.models.user import User
from app.repositories.file import (
    copy,
    delete,
    get_checksum,
    get_filesize,
    get_tmp_path,
    isdir,
    isfile,
)
from app.repositories.orm import ORMRepository
from app.schemas.file_edit import FileEditRequest

log = logging.getLogger(__name__)


async def edit_file(
    session: AsyncSession,
    user: User,
    file_id: int,
    data: FileEditRequest,
) -> File:
    """
    Edit a text file and create a new revision.

    The database is the source of truth. New content is first written
    to a temporary file. The previous current file is copied into the
    revisions storage before the main file is replaced.
    """
    log.info("event=%s file_id=%s", E.FILE_EDIT_STARTED, file_id)

    repository = ORMRepository(session)
    file = await repository.select(File, obj_id=file_id)

    if file is None:
        log.warning("event=%s", E.FILE_EDIT_FILE_NOT_FOUND)
        raise ResourceNotFoundError

    if not file.is_text:
        log.warning("event=%s", E.FILE_EDIT_NOT_TEXT)
        raise ResourceConflictError

    folder = file.file_folder
    parent_chain = await repository.select_parent_chain(folder)

    if (
        folder.is_write_protected or
        folder.is_write_protected_recursive(parent_chain)
    ):
        log.warning("event=%s", E.FILE_EDIT_PARENT_WRITE_PROTECTED)
        raise ResourceLockedError

    file_path = file.get_absolute_path(folder, parent_chain)

    async with locks.lock_file(file_path, LockType.WRITE):
        if await isdir(file_path):
            log.warning("event=%s", E.FILE_EDIT_INCONSISTENT)
            raise ResourceConflictError

        if not await isfile(file_path):
            log.warning("event=%s", E.FILE_EDIT_INCONSISTENT)
            raise ResourceConflictError

        tmp_path = get_tmp_path()
        restore_source_path = None
        file_replaced = False

        try:
            await _write_text(tmp_path, data.content)
            new_filesize = await get_filesize(tmp_path)
            new_checksum = await get_checksum(tmp_path)

        except Exception:
            log.warning("event=%s", E.FILE_EDIT_WRITE_FAILED)
            await _cleanup_path(tmp_path)
            raise ResourceConflictError

        try:
            latest_revision_number = await repository.count_all(
                FileRevision,
                file_id=file.id,
            ) + 1

            revision = FileRevision(
                file_id=file.id,
                created_by=user.id,
                revision_number=latest_revision_number,
                revision_uuid=str(uuid.uuid4()),
                filename=file.filename,
                filesize=file.filesize,
                mimetype=file.mimetype,
                checksum=file.checksum,
            )

            await copy(file_path, revision.absolute_path)
            restore_source_path = revision.absolute_path

            await repository.insert(revision)

            await copy(tmp_path, file_path)
            file_replaced = True

            file.filesize = new_filesize
            file.checksum = new_checksum
            file.updated_by = user.id
            file.latest_revision_number = latest_revision_number

            await repository.update(file)

            await _cleanup_path(tmp_path)
            tmp_path = None

            await write_audit(
                repository=repository,
                event=E.FILE_EDIT_COMPLETED,
                resource_type=File.__tablename__,
                resource_id=file.id,
            )
            await repository.commit()

            restore_source_path = None

        except Exception:
            await repository.rollback()
            await _cleanup_path(tmp_path)

            if restore_source_path is not None:
                if file_replaced:
                    try:
                        await copy(restore_source_path, file_path)
                    except Exception:
                        log.exception("event=%s", E.FILE_EDIT_RESTORE_FAILED)
                    else:
                        await _cleanup_path(restore_source_path)
                else:
                    await _cleanup_path(restore_source_path)

            raise

    log.info("event=%s", E.FILE_EDIT_COMPLETED)
    await hooks.emit(E.FILE_EDIT_COMPLETED, session, file)

    return file


async def _write_text(path: str, content: str) -> None:
    def _write():
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)

    await asyncio.to_thread(_write)


async def _cleanup_path(path: str | None) -> None:
    if path is None:
        return

    try:
        await delete(path)
        log.info("event=%s", E.FILE_EDIT_CLEANUP_COMPLETED)

    except Exception:
        log.exception("event=%s path=%s", E.FILE_EDIT_CLEANUP_FAILED, path)
