# app/services/file_move.py
# SPDX-License-Identifier: GPL-3.0-only

import logging

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.audit import write_audit
from app.config import get_config
from app.constants import FILES_MAX_PATH_LENGTH_BYTES
from app.errors import (
    ResourceConflictError,
    ResourceLockedError,
    ResourceNotFoundError,
)
from app.events import Events as E
from app.hooks import hooks
from app.locks import LockType, locks
from app.models.file import File
from app.models.folder import Folder
from app.models.user import User
from app.repositories.file import isdir, isfile, rename
from app.repositories.orm import ORMRepository
from app.schemas.file_move import FileMoveRequest

log = logging.getLogger(__name__)


# NOTE (ADR-52): File copy is intentionally not supported.
# Files are treated as unique auditable objects. The system supports
# moving files between folders, but does not support cloning a file
# into another independent file object. This preserves a single audit
# lineage for each uploaded file and avoids creating detached copies
# whose access history would need to be reconstructed through copy
# chains.

async def move_file(
    session: AsyncSession,
    user: User,
    file_id: int,
    data: FileMoveRequest,
) -> File:
    """
    Move an existing file to another folder while keeping the database
    record, folder counters, and filesystem projection consistent.

    The database is the source of truth. The primary file is renamed
    from the source folder projection to the destination folder
    projection and restored on failure.
    """
    log.info("event=%s file_id=%s", E.FILE_MOVE_STARTED, file_id)

    config = get_config()
    repository = ORMRepository(session)

    file = await repository.select(File, obj_id=file_id)

    if file is None:
        log.warning("event=%s", E.FILE_MOVE_FILE_NOT_FOUND)
        raise ResourceNotFoundError

    source_folder = file.file_folder
    source_parent_chain = await repository.select_parent_chain(source_folder)

    if (
        source_folder.is_write_protected or
        source_folder.is_write_protected_recursive(source_parent_chain)
    ):
        log.warning("event=%s", E.FILE_MOVE_SOURCE_WRITE_PROTECTED)
        raise ResourceLockedError

    destination_folder = await repository.select(
        Folder,
        obj_id=data.folder_id,
    )

    if destination_folder is None:
        log.warning("event=%s", E.FILE_MOVE_FOLDER_NOT_FOUND)
        raise ResourceNotFoundError

    if source_folder.id == destination_folder.id:
        return file

    destination_parent_chain = await repository.select_parent_chain(
        destination_folder,
    )

    if (
        destination_folder.is_write_protected or
        destination_folder.is_write_protected_recursive(destination_parent_chain)  # noqa: E501
    ):
        log.warning("event=%s", E.FILE_MOVE_DESTINATION_WRITE_PROTECTED)
        raise ResourceLockedError

    source_path = file.get_absolute_path(
        source_folder,
        source_parent_chain,
    )
    destination_path = file.get_absolute_path(
        destination_folder,
        destination_parent_chain,
    )

    if len(destination_path.encode("utf-8")) > FILES_MAX_PATH_LENGTH_BYTES:
        log.warning("event=%s", E.FILE_MOVE_PATH_TOO_LONG)
        raise ResourceConflictError

    async with locks.lock_directory(config.FILES_DIR, LockType.WRITE):
        file_moved = False

        existing_file = await repository.select(
            File,
            filename=file.filename,
            folder_id=destination_folder.id,
        )

        if existing_file is not None:
            log.warning("event=%s", E.FILE_MOVE_FILENAME_CONFLICT)
            raise ResourceConflictError

        if await isdir(destination_path):
            log.warning("event=%s", E.FILE_MOVE_FILENAME_CONFLICT)
            raise ResourceConflictError

        if await isfile(destination_path):
            log.warning("event=%s", E.FILE_MOVE_FILENAME_CONFLICT)
            raise ResourceConflictError

        try:
            await rename(source_path, destination_path)
            file_moved = True

            file.folder_id = destination_folder.id
            file.updated_by = user.id

            source_folder.files_count -= 1
            destination_folder.files_count += 1

            await repository.update(file)
            await repository.update(source_folder)
            await repository.update(destination_folder)

            await write_audit(
                repository=repository,
                event=E.FILE_MOVE_COMPLETED,
                resource_type=File.__tablename__,
                resource_id=file.id,
            )
            await repository.commit()

        except IntegrityError:
            await repository.rollback()

            if file_moved:
                try:
                    await rename(destination_path, source_path)
                except Exception:
                    log.exception("event=%s", E.FILE_MOVE_RESTORE_FAILED)

            log.warning("event=%s", E.FILE_MOVE_FILENAME_CONFLICT)
            raise ResourceConflictError

        except Exception:
            await repository.rollback()

            if file_moved:
                try:
                    await rename(destination_path, source_path)
                except Exception:
                    log.exception("event=%s", E.FILE_MOVE_RESTORE_FAILED)

            raise

    log.info("event=%s", E.FILE_MOVE_COMPLETED)
    await hooks.emit(E.FILE_MOVE_COMPLETED, session, file)

    return file
