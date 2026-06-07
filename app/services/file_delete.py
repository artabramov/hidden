# app/services/file_delete.py
# SPDX-License-Identifier: SSPL-1.0

import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.audit import write_audit
from app.cache.lru import get_thumbnail_cache
from app.errors import ResourceLockedError, ResourceNotFoundError
from app.events import Events as E
from app.hooks import hooks
from app.locks import LockType, locks
from app.models.file import File
from app.models.file_revision import FileRevision
from app.models.file_thumbnail import FileThumbnail
from app.repositories.file import delete, get_tmp_path, rename
from app.repositories.orm import ORMRepository

log = logging.getLogger(__name__)


async def delete_file(
    session: AsyncSession,
    file_id: int,
) -> File:
    """
    Delete an existing file together with its thumbnail and revisions.
    Comments and tags are removed by cascade.

    The database is the source of truth. The primary file is first
    moved to a temporary location and restored on failure. Filesystem
    artifacts are removed after a successful commit.
    """
    log.info("event=%s file_id=%s", E.FILE_DELETE_STARTED, file_id)

    repository = ORMRepository(session)
    file = await repository.select(File, obj_id=file_id)

    if file is None:
        log.warning("event=%s", E.FILE_DELETE_NOT_FOUND)
        raise ResourceNotFoundError

    folder = file.file_folder
    parent_chain = await repository.select_parent_chain(folder)

    if (
        folder.is_write_protected or
        folder.is_write_protected_recursive(parent_chain)
    ):
        log.warning("event=%s", E.FILE_DELETE_PARENT_WRITE_PROTECTED)
        raise ResourceLockedError

    file_path = file.get_absolute_path(folder, parent_chain)
    lock_dir = folder.get_absolute_dir(parent_chain)

    async with locks.lock_directory(lock_dir, LockType.WRITE):
        tmp_path = get_tmp_path()
        file_moved = False

        revisions = await repository.select_all(
            FileRevision,
            file_id=file.id,
        )

        thumbnail = await repository.select(
            FileThumbnail,
            file_id=file.id,
        )

        try:
            await rename(file_path, tmp_path)
            file_moved = True

            if thumbnail is not None:
                await repository.delete(thumbnail)

            for revision in revisions:
                await repository.delete(revision)

            await repository.delete(file)

            folder.files_count -= 1
            await repository.update(folder)

            await write_audit(
                repository=repository,
                event=E.FILE_DELETE_COMPLETED,
                resource_type=File.__tablename__,
                resource_id=file.id,
            )
            await repository.commit()
            get_thumbnail_cache().evict(file.id)

        except Exception:
            await repository.rollback()

            file_restored = False

            if file_moved:
                try:
                    await rename(tmp_path, file_path)
                    file_restored = True
                except Exception:
                    log.exception("event=%s", E.FILE_DELETE_RESTORE_FAILED)

            if not file_restored:
                try:
                    await delete(tmp_path)
                except Exception:
                    log.exception("event=%s", E.FILE_DELETE_CLEANUP_TMP_FAILED)

            raise

        try:
            await delete(tmp_path)
        except Exception:
            log.exception("event=%s", E.FILE_DELETE_CLEANUP_TMP_FAILED)

        if thumbnail is not None:
            try:
                await delete(thumbnail.absolute_path)
            except Exception:
                log.exception("event=%s", E.FILE_DELETE_CLEANUP_THUMBNAIL_FAILED)  # noqa: E501

        for revision in revisions:
            try:
                await delete(revision.absolute_path)
            except Exception:
                log.exception("event=%s", E.FILE_DELETE_CLEANUP_REVISION_FAILED)  # noqa: E501

    log.info("event=%s", E.FILE_DELETE_COMPLETED)
    await hooks.emit(E.FILE_DELETE_COMPLETED, session, file)

    return file
