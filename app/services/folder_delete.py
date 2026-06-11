# app/services/folder_delete.py
# SPDX-License-Identifier: GPL-3.0-only

import logging

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
from app.models.folder import Folder
from app.repositories.file import rmdir
from app.repositories.orm import ORMRepository
from app.services.file_delete import delete_file

log = logging.getLogger(__name__)


# NOTE (ADR-64): Folder deletion is not an atomic operation.
# 1. Direct files are deleted first (each file deletion is atomic on
#    its own), and only after that the folder itself is removed. If file
#    deletion fails, the folder remains in its current state and already
#    deleted files are not restored.
# 2. In rare failure cases after successful filesystem deletion (rmdir)
#    but before the database commit, the system may become inconsistent:
#    the directory is removed while the database record still exists.
#    This condition is logged and is not automatically compensated.

async def delete_folder(
    session: AsyncSession,
    folder_id: int,
) -> Folder:
    """
    Delete a folder and all direct files inside it. Subfolders are
    never deleted recursively. If the folder contains direct subfolders,
    deletion fails with a conflict.
    """
    log.info("event=%s folder_id=%s", E.FOLDER_DELETE_STARTED, folder_id)

    repository = ORMRepository(session)
    folder = await repository.select(Folder, obj_id=folder_id)

    if folder is None:
        log.warning("event=%s", E.FOLDER_DELETE_FOLDER_NOT_FOUND)
        raise ResourceNotFoundError

    parent_chain = await repository.select_parent_chain(folder)

    if (
        folder.is_write_protected or
        folder.is_write_protected_recursive(parent_chain)
    ):
        log.warning("event=%s", E.FOLDER_DELETE_WRITE_PROTECTED)
        raise ResourceLockedError

    if folder.children_count > 0:
        log.warning("event=%s", E.FOLDER_DELETE_HAS_FOLDERS)
        raise ResourceConflictError

    files = await repository.select_all(File, folder_id=folder.id)

    for file in files:
        await delete_file(
            session=session,
            file_id=file.id,
        )

    folder = await repository.select(Folder, obj_id=folder_id)

    if folder is None:
        log.warning("event=%s", E.FOLDER_DELETE_FOLDER_NOT_FOUND)
        raise ResourceNotFoundError

    parent_chain = await repository.select_parent_chain(folder)

    if (
        folder.is_write_protected or
        folder.is_write_protected_recursive(parent_chain)
    ):
        log.warning("event=%s", E.FOLDER_DELETE_WRITE_PROTECTED)
        raise ResourceLockedError

    if folder.children_count > 0:
        log.warning("event=%s", E.FOLDER_DELETE_HAS_FOLDERS)
        raise ResourceConflictError

    if folder.files_count > 0:
        log.warning("event=%s", E.FOLDER_DELETE_HAS_FILES)
        raise ResourceConflictError

    absolute_dir = folder.get_absolute_dir(parent_chain)
    parent = parent_chain[0] if parent_chain else None

    if parent is not None:
        lock_dir = parent.get_absolute_dir(parent_chain[1:])
    else:
        lock_dir = absolute_dir

    async with locks.lock_directory(lock_dir, LockType.WRITE):

        try:
            await rmdir(absolute_dir)

        except Exception:
            await repository.rollback()
            log.exception("event=%s", E.FOLDER_DELETE_FAILED)
            raise

        try:
            await repository.delete(folder)

            if parent is not None:
                parent.children_count -= 1
                await repository.update(parent)

            await write_audit(
                repository=repository,
                event=E.FOLDER_DELETE_COMPLETED,
                resource_type=Folder.__tablename__,
                resource_id=folder.id,
            )
            await repository.commit()

        except Exception:
            await repository.rollback()
            log.exception("event=%s", E.FOLDER_DELETE_INCONSISTENT)
            raise

    log.info("event=%s", E.FOLDER_DELETE_COMPLETED)
    await hooks.emit(E.FOLDER_DELETE_COMPLETED, session, folder)

    return folder
