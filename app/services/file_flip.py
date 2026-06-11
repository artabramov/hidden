# app/services/file_flip.py
# SPDX-License-Identifier: GPL-3.0-only

import logging
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.audit import write_audit
from app.cache.lru import get_thumbnail_cache
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
from app.models.file_thumbnail import FileThumbnail
from app.models.user import User
from app.repositories.file import (
    copy,
    delete,
    get_checksum,
    get_filesize,
    get_mimetype,
    get_tmp_path,
    isdir,
    isfile,
)
from app.repositories.image import (
    create_thumbnail,
)
from app.repositories.image import flip as flip_image
from app.repositories.image import (
    get_image_size,
)
from app.repositories.orm import ORMRepository
from app.schemas.file_flip import FileFlipRequest

log = logging.getLogger(__name__)


async def flip_file(
    session: AsyncSession,
    user: User,
    file_id: int,
    data: FileFlipRequest,
) -> File:
    """
    Flip an existing image file and create a new revision from the
    previous current state.

    The database is the source of truth. Flip output is first written
    to a temporary file. The previous current file is copied into the
    revisions storage before the main file is replaced.

    Thumbnail update is post-commit and best-effort, following the same
    pattern as file upload.
    """
    log.info("event=%s file_id=%s", E.FILE_FLIP_STARTED, file_id)

    repository = ORMRepository(session)
    file = await repository.select(File, obj_id=file_id)

    if file is None:
        log.warning("event=%s", E.FILE_FLIP_FILE_NOT_FOUND)
        raise ResourceNotFoundError

    if not file.is_image:
        log.warning("event=%s", E.FILE_FLIP_NOT_IMAGE)
        raise ResourceConflictError

    folder = file.file_folder
    parent_chain = await repository.select_parent_chain(folder)

    if (
        folder.is_write_protected or
        folder.is_write_protected_recursive(parent_chain)
    ):
        log.warning("event=%s", E.FILE_FLIP_PARENT_WRITE_PROTECTED)
        raise ResourceLockedError

    file_path = file.get_absolute_path(folder, parent_chain)
    async with locks.lock_file(file_path, LockType.WRITE):

        if await isdir(file_path):
            log.warning("event=%s", E.FILE_FLIP_INCONSISTENT)
            raise ResourceConflictError

        if not await isfile(file_path):
            log.warning("event=%s", E.FILE_FLIP_INCONSISTENT)
            raise ResourceConflictError

        tmp_path = get_tmp_path()
        restore_source_path = None
        file_replaced = False

        try:
            await flip_image(file_path, tmp_path, data.axis)
            flipped_filesize = await get_filesize(tmp_path)
            flipped_mimetype = await get_mimetype(tmp_path)
            flipped_checksum = await get_checksum(tmp_path)

        except Exception:
            log.warning("event=%s", E.FILE_FLIP_UNSUPPORTED_IMAGE)
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

            file.filesize = flipped_filesize
            file.mimetype = flipped_mimetype
            file.checksum = flipped_checksum
            file.updated_by = user.id
            file.latest_revision_number = latest_revision_number

            await repository.update(file)

            await _cleanup_path(tmp_path)
            tmp_path = None

            await write_audit(
                repository=repository,
                event=E.FILE_FLIP_COMPLETED,
                resource_type=File.__tablename__,
                resource_id=file.id,
            )
            await repository.commit()
            get_thumbnail_cache().evict(file.id)

            restore_source_path = None

        except Exception:
            await repository.rollback()
            await _cleanup_path(tmp_path)

            if restore_source_path is not None:
                if file_replaced:
                    try:
                        await copy(restore_source_path, file_path)
                    except Exception:
                        log.exception("event=%s", E.FILE_FLIP_RESTORE_FAILED)
                    else:
                        await _cleanup_path(restore_source_path)
                else:
                    await _cleanup_path(restore_source_path)

            raise

        thumbnail_creation_blocked = False
        old_thumbnail = await repository.select(
            FileThumbnail,
            file_id=file.id,
        )

        if old_thumbnail is not None:
            old_thumbnail_path = old_thumbnail.absolute_path

            try:
                await repository.delete(old_thumbnail, flush=False)
                await repository.commit()

            except Exception:
                await repository.rollback()
                log.exception("event=%s", E.FILE_FLIP_THUMBNAIL_FAILED)
                thumbnail_creation_blocked = True

            else:
                file.file_thumbnail = None
                await _cleanup_path(old_thumbnail_path)

        if file.is_image and not thumbnail_creation_blocked:
            thumbnail_path = None

            try:
                thumbnail = FileThumbnail(
                    file_id=file.id,
                    created_by=user.id,
                    thumbnail_uuid=str(uuid.uuid4()),
                    filesize=0,
                    mimetype=None,
                    width=0,
                    height=0,
                )

                await create_thumbnail(file_path, thumbnail.absolute_path)
                thumbnail_path = thumbnail.absolute_path

                thumbnail.filesize = await get_filesize(
                    thumbnail.absolute_path,
                )
                thumbnail.mimetype = await get_mimetype(
                    thumbnail.absolute_path,
                )
                thumbnail.width, thumbnail.height = await get_image_size(
                    thumbnail.absolute_path,
                )

                await repository.insert(thumbnail, flush=False)
                await repository.commit()

                file.file_thumbnail = thumbnail

            except Exception:
                await repository.rollback()
                log.exception("event=%s", E.FILE_FLIP_THUMBNAIL_FAILED)
                await _cleanup_path(thumbnail_path)

    log.info("event=%s", E.FILE_FLIP_COMPLETED)
    await hooks.emit(E.FILE_FLIP_COMPLETED, session, file)

    return file


async def _cleanup_path(path: str | None) -> None:
    """
    Delete a filesystem path if it was created. Cleanup is best-effort.
    """
    if path is None:
        return

    try:
        await delete(path)
        log.info("event=%s", E.FILE_FLIP_CLEANUP_COMPLETED)

    except Exception:
        log.exception("event=%s path=%s", E.FILE_FLIP_CLEANUP_FAILED, path)
