# app/services/file_upload.py
# SPDX-License-Identifier: GPL-3.0-only

import logging
import uuid

from fastapi import UploadFile
from pydantic_core import PydanticCustomError
from sqlalchemy.ext.asyncio import AsyncSession

from app.audit import write_audit
from app.cache.lru import get_thumbnail_cache
from app.constants import FILES_MAX_PATH_LENGTH_BYTES
from app.errors import (
    ResourceConflictError,
    ResourceLockedError,
    ResourceNotFoundError,
    ValueInvalidError,
)
from app.events import Events as E
from app.hooks import hooks
from app.locks import LockType, locks
from app.models.file import File
from app.models.file_revision import FileRevision
from app.models.file_thumbnail import FileThumbnail
from app.models.folder import Folder
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
    isimage,
    upload,
)
from app.repositories.image import (
    create_thumbnail,
    get_image_size,
)
from app.repositories.orm import ORMRepository
from app.validators.path_segment import validate_path_segment

log = logging.getLogger(__name__)


# NOTE (ADR-47): File mutations under overlapping WRITE lock.
# Any operation that modifies a file or its attributes must be executed
# under a WRITE lock that overlaps the target file. This ensures that
# filesystem changes and corresponding DB updates are serialized and
# remain consistent. The lock may be acquired either on the file itself
# or on a directory covering the file.

# NOTE (ADR-48): File upload cleanup is best-effort.
# If the process terminates between file write and cleanup, an orphaned
# file may remain on disk. This is considered unlikely and accepted,
# as the database is the source of truth.

# NOTE (ADR-49): Files cannot be uploaded to root.
# Every file must have a parent folder (folder_id is required).
# Root is not treated as a file container.

# TODO: Prevent resource exhaustion by enforcing size limits for upload,
# text edit, and image operations.

# TODO: Strip image metadata on upload (EXIF, XMP, IPTC). Photos
# routinely carry GPS coordinates, camera serial number, and device
# identifiers; for a privacy-oriented store these should not be
# persisted by default. Pillow is already in the upload pipeline for
# thumbnail generation, so a re-save without metadata fits naturally
# there. Make it configurable (per-instance or per-user opt-out) so
# users who deliberately need EXIF preserved can keep it.

# TODO: Add background integrity scan for encrypted storage consistency.
# The scan should periodically verify:
# 1. Referenced files exist on the filesystem;
# 2. Filesystem objects have corresponding database entries;
# 3. File revisions are structurally consistent;
# 4. Generated thumbnails exist and remain linked correctly;
# 5. Stored hashes match actual file contents.

# TODO: Add soft filesystem capacity guard for uploads. Refuse new
# uploads when available disk space falls below a configured minimum
# threshold.


async def upload_file(
    session: AsyncSession,
    user: User,
    folder_id: int,
    uploaded_file: UploadFile,
) -> File:
    """
    Upload a file into an existing folder. The operation is
    transactional at the DB level and reconciles filesystem state
    on failure. All writes are staged through a temporary file and
    applied under a directory lock.

    (1) upload file to temporary path
    (2) read real file metadata (size, mimetype, checksum)

    if file does not exist:
        (3) write main file
        (4) insert file record

    if file exists:
        (3) copy current file as a restore source
        (4) insert revision record
        (5) overwrite main file
        (6) update file record

    (7) write audit
    (8) commit

    On failure of the main transaction, the session is rolled back and
    filesystem state is reconciled: temporary data is removed, new files
    are deleted, or the original file is restored from the saved copy.

    After a successful commit, thumbnail processing is performed as a
    separate best-effort step:

    (9) delete previous thumbnail record and then its file
    (10) create new thumbnail file (if applicable)
    (11) read thumbnail metadata
    (12) insert thumbnail record

    Thumbnail failures do not affect the main upload result. Errors
    are logged, partial files are cleaned up when possible, and the
    operation completes without a thumbnail if necessary.
    """
    log.info("event=%s folder_id=%s", E.FILE_UPLOAD_STARTED, folder_id)

    repository = ORMRepository(session)
    folder = await repository.select(Folder, obj_id=folder_id)

    if folder is None:
        log.warning("event=%s", E.FILE_UPLOAD_FOLDER_NOT_FOUND)
        raise ResourceNotFoundError

    parent_chain = await repository.select_parent_chain(folder)

    if (
        folder.is_write_protected or
        folder.is_write_protected_recursive(parent_chain)
    ):
        log.warning("event=%s", E.FILE_UPLOAD_FOLDER_WRITE_PROTECTED)
        raise ResourceLockedError

    try:
        filename = validate_path_segment(uploaded_file.filename)

    except PydanticCustomError:
        log.warning("event=%s", E.FILE_UPLOAD_FILENAME_INVALID)
        raise ValueInvalidError(
            field="file",
            input_value=uploaded_file.filename,
        )

    file = File(
        folder_id=folder.id,
        created_by=user.id,
        filename=filename,
        filesize=0,
        mimetype=None,
        checksum="",
        summary=None,
    )

    file_path = file.get_absolute_path(folder, parent_chain)

    if len(file_path.encode("utf-8")) > FILES_MAX_PATH_LENGTH_BYTES:
        log.warning("event=%s", E.FILE_UPLOAD_PATH_TOO_LONG)
        raise ResourceConflictError

    # Stage upload into a temporary file and probe its properties.
    # The temp file is the single source for size/mimetype/checksum
    # before any mutation of the target directory.

    tmp_path = get_tmp_path()

    try:
        await upload(uploaded_file, tmp_path)
        file_filesize = await get_filesize(tmp_path)
        file_mimetype = await get_mimetype(tmp_path)
        file_checksum = await get_checksum(tmp_path)

    except Exception:
        await _cleanup_path(tmp_path)
        raise

    # Acquire directory lock to serialize all mutations of this folder.
    # From this point, DB state and filesystem must be kept in sync.

    lock_dir = folder.get_absolute_dir(parent_chain)
    async with locks.lock_directory(lock_dir, LockType.WRITE):

        # Validate DB/FS consistency and detect filename conflicts
        # before performing any write. All conflict flows must leave
        # no side effects.

        if await isdir(file_path):
            await _cleanup_path(tmp_path)
            tmp_path = None

            log.warning("event=%s", E.FILE_UPLOAD_FILENAME_CONFLICT)
            raise ResourceConflictError

        existing_file = await repository.select(
            File,
            filename=filename,
            folder_id=folder.id,
        )

        if existing_file is None and await isfile(file_path):
            await _cleanup_path(tmp_path)
            tmp_path = None

            log.warning("event=%s", E.FILE_UPLOAD_FILENAME_CONFLICT)
            raise ResourceConflictError

        if (
            existing_file is not None
            and existing_file.mimetype != file_mimetype
        ):
            await _cleanup_path(tmp_path)
            tmp_path = None

            log.warning("event=%s", E.FILE_UPLOAD_FILENAME_CONFLICT)
            raise ResourceConflictError

        # One rollback handler inside the lock clears tmp, then aligns
        # disk with the rolled-back session: remove newly written main
        # file or restore main from the saved copy. The restore source
        # is preserved if restoration fails.

        written_main_path = None
        restore_source_path = None
        file_replaced = False

        # Single transactional block: apply filesystem changes; update
        # DB state; write audit and commit. Thumbnail processing is
        # handled after commit as a separate best-effort step.
        # Any failure triggers rollback + disk compensation below.

        result_file = None

        try:
            # New file flow: write main file first, then persist DB
            # record. On rollback, the main file must be removed.

            if existing_file is None:
                await copy(tmp_path, file_path)
                written_main_path = file_path

                file.filesize = file_filesize
                file.mimetype = file_mimetype
                file.checksum = file_checksum
                await repository.insert(file)

                folder.files_count += 1
                await repository.update(folder)

                await _cleanup_path(tmp_path)
                tmp_path = None

                result_file = file

            # Revision flow: copy current file as a restore source, then
            # overwrite main file and update DB. On rollback: restore
            # main from the saved copy if overwrite happened; otherwise
            # just remove the saved copy.

            else:
                latest_revision_number = await repository.count_all(
                    FileRevision,
                    file_id=existing_file.id,
                ) + 1

                # Revision numbering depends on the directory WRITE
                # lock. Uploads into the same folder are serialized,
                # so count + 1 is safe for files in that folder.

                revision = FileRevision(
                    file_id=existing_file.id,
                    created_by=user.id,
                    revision_number=latest_revision_number,
                    revision_uuid=str(uuid.uuid4()),
                    filename=existing_file.filename,
                    filesize=existing_file.filesize,
                    mimetype=existing_file.mimetype,
                    checksum=existing_file.checksum,
                )

                await copy(file_path, revision.absolute_path)
                restore_source_path = revision.absolute_path

                await repository.insert(revision)

                await copy(tmp_path, file_path)
                file_replaced = True

                existing_file.filesize = file_filesize
                existing_file.mimetype = file_mimetype
                existing_file.checksum = file_checksum
                existing_file.updated_by = user.id
                existing_file.latest_revision_number = latest_revision_number

                await repository.update(existing_file)

                await _cleanup_path(tmp_path)
                tmp_path = None

                result_file = existing_file

            # Finalize transaction: audit and commit.
            # After this point, DB state becomes authoritative.

            await write_audit(
                repository=repository,
                event=E.FILE_UPLOAD_COMPLETED,
                resource_type=File.__tablename__,
                resource_id=result_file.id,
            )
            await repository.commit()
            get_thumbnail_cache().evict(result_file.id)

            written_main_path = None
            restore_source_path = None

        except Exception:

            # Rollback DB and reconcile filesystem: remove temp file;
            # remove newly written main file or restore main from the
            # saved copy. The restore source is preserved if restoration
            # fails.

            await repository.rollback()
            await _cleanup_path(tmp_path)

            if written_main_path is not None:
                await _cleanup_path(written_main_path)

            if restore_source_path is not None:
                if file_replaced:
                    try:
                        await copy(restore_source_path, file_path)
                    except Exception:
                        log.exception("event=%s", E.FILE_UPLOAD_RESTORE_FAILED)
                    else:
                        await _cleanup_path(restore_source_path)
                else:
                    await _cleanup_path(restore_source_path)

            raise

        # Thumbnail update is post-commit and best-effort. The main
        # upload/revision transaction must not depend on preview
        # artifact generation. If removal of an existing thumbnail
        # fails, creation of a new one is skipped to avoid conflicts
        # and keep DB state consistent.

        thumbnail_creation_blocked = False
        old_thumbnail = await repository.select(
            FileThumbnail,
            file_id=result_file.id,
        )

        if old_thumbnail is not None:
            old_thumbnail_path = old_thumbnail.absolute_path

            try:
                await repository.delete(old_thumbnail, flush=False)
                await repository.commit()

            except Exception:
                await repository.rollback()
                log.exception("event=%s", E.FILE_UPLOAD_THUMBNAIL_FAILED)
                thumbnail_creation_blocked = True

            else:
                result_file.file_thumbnail = None
                await _cleanup_path(old_thumbnail_path)

        if isimage(file_mimetype) and not thumbnail_creation_blocked:
            thumbnail_path = None

            try:
                thumbnail = FileThumbnail(
                    file_id=result_file.id,
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

                result_file.file_thumbnail = thumbnail

            except Exception:
                await repository.rollback()
                log.exception("event=%s", E.FILE_UPLOAD_THUMBNAIL_FAILED)
                await _cleanup_path(thumbnail_path)

    log.info("event=%s file_id=%s", E.FILE_UPLOAD_COMPLETED, result_file.id)
    await hooks.emit(E.FILE_UPLOAD_COMPLETED, session, result_file)
    return result_file


async def _cleanup_path(path: str | None) -> None:
    """
    Delete a filesystem path if it was created. Cleanup is best-effort:
    failures are logged and do not affect the main flow. The path is
    included in logs only on failure for diagnostic purposes.
    """
    if path is None:
        return

    try:
        await delete(path)
        log.info("event=%s", E.FILE_UPLOAD_CLEANUP_COMPLETED)

    except Exception:
        log.exception("event=%s path=%s", E.FILE_UPLOAD_CLEANUP_FAILED, path)
