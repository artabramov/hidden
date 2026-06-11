# app/services/file_update.py
# SPDX-License-Identifier: GPL-3.0-only

import logging

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.audit import write_audit
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
from app.models.user import User
from app.repositories.file import isdir, isfile, rename
from app.repositories.orm import ORMRepository
from app.schemas.file_update import FileUpdateRequest

log = logging.getLogger(__name__)


async def update_file(
    session: AsyncSession,
    user: User,
    file_id: int,
    data: FileUpdateRequest,
) -> File:
    """
    Update file filename and optional summary while keeping the database
    record and filesystem projection consistent.
    """
    log.info("event=%s file_id=%s", E.FILE_UPDATE_STARTED, file_id)

    repository = ORMRepository(session)
    file = await repository.select(File, obj_id=file_id)

    if file is None:
        log.warning("event=%s", E.FILE_UPDATE_FILE_NOT_FOUND)
        raise ResourceNotFoundError

    folder = file.file_folder
    parent_chain = await repository.select_parent_chain(folder)

    if (
        folder.is_write_protected or
        folder.is_write_protected_recursive(parent_chain)
    ):
        log.warning("event=%s", E.FILE_UPDATE_PARENT_WRITE_PROTECTED)
        raise ResourceLockedError

    old_absolute_path = file.get_absolute_path(folder, parent_chain)

    old_filename = file.filename
    file.filename = data.filename
    file.updated_by = user.id

    if "summary" in data.model_fields_set:
        file.summary = data.summary

    new_absolute_path = file.get_absolute_path(folder, parent_chain)

    if len(new_absolute_path.encode("utf-8")) > FILES_MAX_PATH_LENGTH_BYTES:
        log.warning("event=%s", E.FILE_UPDATE_PATH_TOO_LONG)
        file.filename = old_filename
        raise ResourceConflictError

    lock_dir = folder.get_absolute_dir(parent_chain)

    async with locks.lock_directory(lock_dir, LockType.WRITE):
        file_renamed = False

        if old_absolute_path != new_absolute_path:
            if await isdir(new_absolute_path):
                log.warning("event=%s", E.FILE_UPDATE_FILENAME_CONFLICT)
                file.filename = old_filename
                raise ResourceConflictError

            if await isfile(new_absolute_path):
                log.warning("event=%s", E.FILE_UPDATE_FILENAME_CONFLICT)
                file.filename = old_filename
                raise ResourceConflictError

        try:
            await repository.update(file)

            if old_absolute_path != new_absolute_path:
                await rename(old_absolute_path, new_absolute_path)
                file_renamed = True

            await write_audit(
                repository=repository,
                event=E.FILE_UPDATE_COMPLETED,
                resource_type=File.__tablename__,
                resource_id=file.id,
            )
            await repository.commit()

        except IntegrityError:
            log.warning("event=%s", E.FILE_UPDATE_FILENAME_CONFLICT)
            await repository.rollback()

            if file_renamed:
                try:
                    await rename(new_absolute_path, old_absolute_path)
                except Exception:
                    log.exception("event=%s", E.FILE_UPDATE_RESTORE_FAILED)

            raise ResourceConflictError

        except Exception:
            await repository.rollback()

            if file_renamed:
                try:
                    await rename(new_absolute_path, old_absolute_path)
                except Exception:
                    log.exception("event=%s", E.FILE_UPDATE_RESTORE_FAILED)

            raise

    log.info("event=%s", E.FILE_UPDATE_COMPLETED)
    await hooks.emit(E.FILE_UPDATE_COMPLETED, session, file)

    return file
