# app/services/folder_create.py
# SPDX-License-Identifier: SSPL-1.0

import logging

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.audit import write_audit
from app.config import get_config
from app.constants import (
    FILES_MAX_FOLDER_DEPTH,
    FILES_MAX_PATH_LENGTH_BYTES,
)
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
from app.repositories.file import isdir, isfile, mkdir, rmdir
from app.repositories.orm import ORMRepository
from app.schemas.folder_create import FolderCreateRequest

log = logging.getLogger(__name__)


async def create_folder(
    session: AsyncSession,
    user: User,
    data: FolderCreateRequest,
) -> Folder:
    """
    Create a folder in the root or under the given parent folder by
    validating parent existence, enforcing recursive write protection,
    acquiring a directory-level write lock on the target parent (or
    root), inserting the folder record, creating the filesystem
    projection, writing audit, committing the transaction, and
    emitting post-commit hooks.
    """
    log.info("event=%s parent_id=%s", E.FOLDER_CREATE_STARTED, data.parent_id)

    repository = ORMRepository(session)
    config = get_config()

    parent = None
    parent_dir = config.FILES_DIR
    parent_chain = tuple()

    if data.parent_id is not None:
        parent = await repository.select(Folder, obj_id=data.parent_id)

        if parent is None:
            log.warning("event=%s", E.FOLDER_CREATE_PARENT_NOT_FOUND)
            raise ResourceNotFoundError

        parent_chain = await repository.select_parent_chain(parent)
        if (
            parent.is_write_protected or
            parent.is_write_protected_recursive(parent_chain)
        ):
            log.warning("event=%s", E.FOLDER_CREATE_PARENT_WRITE_PROTECTED)
            raise ResourceLockedError

        if len(parent_chain) + 1 > FILES_MAX_FOLDER_DEPTH:
            log.warning("event=%s", E.FOLDER_CREATE_DEPTH_LIMIT_EXCEEDED)
            raise ResourceConflictError

        parent_dir = parent.get_absolute_dir(parent_chain)

    async with locks.lock_directory(parent_dir, LockType.WRITE):
        directory_created = False
        folder = Folder(
            parent_id=data.parent_id,
            created_by=user.id,
            dirname=data.dirname,
            summary=data.summary,
        )

        folder_chain = (parent, *parent_chain) if parent is not None else ()
        absolute_dir = folder.get_absolute_dir(folder_chain)

        if len(absolute_dir.encode("utf-8")) > FILES_MAX_PATH_LENGTH_BYTES:
            log.warning("event=%s", E.FOLDER_CREATE_PATH_TOO_LONG)
            raise ResourceConflictError

        if await isdir(absolute_dir):
            log.warning("event=%s", E.FOLDER_CREATE_DIRNAME_CONFLICT)
            raise ResourceConflictError

        if await isfile(absolute_dir):
            log.warning("event=%s", E.FOLDER_CREATE_DIRNAME_CONFLICT)
            raise ResourceConflictError

        try:
            await repository.insert(folder)

            if parent is not None:
                parent.children_count += 1
                await repository.update(parent)

        except IntegrityError:
            log.warning("event=%s", E.FOLDER_CREATE_DIRNAME_CONFLICT)
            await repository.rollback()
            raise ResourceConflictError

        try:
            await mkdir(absolute_dir)
            directory_created = True

            await write_audit(
                repository=repository,
                event=E.FOLDER_CREATE_COMPLETED,
                resource_type=Folder.__tablename__,
                resource_id=folder.id,
            )
            await repository.commit()

        except Exception:
            await repository.rollback()

            if directory_created:
                try:
                    await rmdir(absolute_dir)
                except Exception:
                    log.exception("event=%s", E.FOLDER_CREATE_CLEANUP_FAILED)

            raise

    log.info("event=%s folder_id=%s", E.FOLDER_CREATE_COMPLETED, folder.id)
    await hooks.emit(E.FOLDER_CREATE_COMPLETED, session, folder)

    return folder
