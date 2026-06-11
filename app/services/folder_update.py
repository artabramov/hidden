# app/services/folder_update.py
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
from app.models.folder import Folder
from app.models.user import User
from app.repositories.file import isdir, isfile, rename
from app.repositories.orm import ORMRepository
from app.schemas.folder_update import FolderUpdateRequest

log = logging.getLogger(__name__)


async def update_folder(
    session: AsyncSession,
    user: User,
    folder_id: int,
    data: FolderUpdateRequest,
) -> Folder:
    """
    Update folder dirname and optional summary while keeping the
    database record and filesystem directory projection consistent.
    """
    log.info("event=%s folder_id=%s", E.FOLDER_UPDATE_STARTED, folder_id)

    cfg = get_config()
    repository = ORMRepository(session)
    folder = await repository.select(Folder, obj_id=folder_id)

    if folder is None:
        log.warning("event=%s", E.FOLDER_UPDATE_FOLDER_NOT_FOUND)
        raise ResourceNotFoundError

    parent_chain = await repository.select_parent_chain(folder)

    if (
        folder.is_write_protected or
        folder.is_write_protected_recursive(parent_chain)
    ):
        log.warning("event=%s", E.FOLDER_UPDATE_WRITE_PROTECTED)
        raise ResourceLockedError

    old_absolute_dir = folder.get_absolute_dir(parent_chain)
    folder.dirname = data.dirname
    folder.updated_by = user.id

    if "summary" in data.model_fields_set:
        folder.summary = data.summary

    new_absolute_dir = folder.get_absolute_dir(parent_chain)

    if len(new_absolute_dir.encode("utf-8")) > FILES_MAX_PATH_LENGTH_BYTES:
        log.warning("event=%s", E.FOLDER_UPDATE_PATH_TOO_LONG)
        raise ResourceConflictError

    if parent_chain:
        parent = parent_chain[0]
        lock_dir = parent.get_absolute_dir(parent_chain[1:])
    else:
        lock_dir = cfg.FILES_DIR

    async with locks.lock_directory(lock_dir, LockType.WRITE):
        directory_renamed = False

        if old_absolute_dir != new_absolute_dir:
            if await isdir(new_absolute_dir):
                log.warning("event=%s", E.FOLDER_UPDATE_DIRNAME_CONFLICT)
                raise ResourceConflictError

            if await isfile(new_absolute_dir):
                log.warning("event=%s", E.FOLDER_UPDATE_DIRNAME_CONFLICT)
                raise ResourceConflictError

        try:
            await repository.update(folder)

            if old_absolute_dir != new_absolute_dir:
                await rename(old_absolute_dir, new_absolute_dir)
                directory_renamed = True

            await write_audit(
                repository=repository,
                event=E.FOLDER_UPDATE_COMPLETED,
                resource_type=Folder.__tablename__,
                resource_id=folder.id,
            )
            await repository.commit()

        except IntegrityError:
            log.warning("event=%s", E.FOLDER_UPDATE_DIRNAME_CONFLICT)
            await repository.rollback()
            raise ResourceConflictError

        except Exception:
            await repository.rollback()

            if directory_renamed:
                try:
                    await rename(new_absolute_dir, old_absolute_dir)
                except Exception:
                    log.exception("event=%s", E.FOLDER_UPDATE_ROLLBACK_FAILED)

            raise

    log.info("event=%s", E.FOLDER_UPDATE_COMPLETED)
    await hooks.emit(E.FOLDER_UPDATE_COMPLETED, session, folder)

    return folder
