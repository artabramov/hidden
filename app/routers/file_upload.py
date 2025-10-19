"""FastAPI router for file uploading."""

import os
import uuid
from fastapi import (
    APIRouter, UploadFile, Request, Depends, Path, status, File as Data
)
from fastapi.responses import JSONResponse
from app.sqlite import get_session
from app.redis import get_cache
from app.models.user import User, UserRole
from app.models.file import File
from app.models.file_revision import FileRevision
from app.models.file_thumbnail import FileThumbnail
from app.models.folder import Folder
from app.schemas.file_upload import FileUploadResponse
from app.helpers.image_helper import image_resize, IMAGE_MIMETYPES
from app.validators.file_validators import name_validate
from app.repository import Repository
from app.hook import Hook, HOOK_AFTER_FILE_UPLOAD
from app.auth import auth
from app.error import (
    E, LOC_PATH, LOC_BODY, ERR_VALUE_NOT_FOUND, ERR_FILE_MIMETYPE_INVALID,
    ERR_VALUE_INVALID, ERR_FILE_CONFLICT, ERR_VALUE_READONLY)

router = APIRouter()


@router.post(
    "/folder/{folder_id}/file",
    status_code=status.HTTP_201_CREATED,
    response_class=JSONResponse,
    response_model=FileUploadResponse,
    summary="Upload file",
    tags=["Files"]
)
async def file_upload(
    request: Request,
    folder_id: int = Path(..., ge=1),
    data: UploadFile = Data(...),
    session=Depends(get_session),
    cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.writer))
) -> FileUploadResponse:
    """
    Uploads a file into the target folder. If no file with that name
    exists, a new one is created; if it does, the current head file
    is snapshotted as a new immutable revision and the upload becomes
    the new head. File metadata (size, MIME type, checksum) is computed
    from the uploaded content and persisted. Disk writes are performed
    via a temporary file followed by an atomic rename to avoid partial
    states.

    This operation is serialized per (folder_id, filename) using an
    in-process asyncio lock, so concurrent uploads of the same name in a
    single process are executed one by one. In the update path, if the
    database commit fails after the head file was already replaced on
    disk, the previous head is restored from the just-created revision
    to keep the filesystem and database consistent. Thumbnails are
    regenerated for image types inside the same critical section after
    a successful commit; any outdated thumbnail is removed first.

    **Authentication:**
    - Requires a valid bearer token with `writer` role or higher.

    **Validation schemas:**
    - `FileUploadResponse` — contains the newly created (or updated)
    file ID and the latest revision number.

    **Path parameters:**
    - `folder_id` (integer ≥ 1) — target folder identifier.

    **Request body:**
    - `file` — the file to upload (`multipart/form-data`).

    **Response codes:**
    - `201` — file successfully uploaded; file created or replaced
    (revision recorded when replaced); thumbnail generated or skipped.
    - `401` — missing, invalid, or expired token.
    - `403` — insufficient role to perform the operation, invalid JTI,
    user is inactive or suspended.
    - `404` — folder not found.
    - `409` — conflict on DB/FS mismatch for the file (file present but
    file missing, or vice versa; MIME type changed for an existing file).
    - `422` — invalid file name.
    - `423` — application is temporarily locked.
    - `498` — gocryptfs key is missing.
    - `499` — gocryptfs key is invalid.

    **Hooks:**
    - `HOOK_AFTER_FILE_UPLOAD`: executed after a successful upload.
    """
    config = request.app.state.config
    file_manager = request.app.state.file_manager
    lru = request.app.state.lru

    folder_locks = request.app.state.folder_locks
    file_locks = request.app.state.file_locks

    temporary_filename = str(uuid.uuid4()) + ".tmp"
    temporary_path = os.path.join(config.TEMPORARY_DIR, temporary_filename)

    file_renamed = False
    file_replaced = False
    thumbnail_path = None

    try:
        filename = name_validate(data.filename)
    except ValueError:
        raise E([LOC_BODY, "file"], data.filename, ERR_VALUE_INVALID,
                status.HTTP_422_UNPROCESSABLE_ENTITY)

    # NOTE: On file upload, acquire the folder READ lock first,
    # then the per-file exclusive lock.

    folder_lock = folder_locks[folder_id]
    file_lock_key = (folder_id, filename)
    file_lock = file_locks[file_lock_key]
    async with folder_lock.read(), file_lock:

        # Ensure the folder exists
        folder_repository = Repository(session, cache, Folder, config)
        folder = await folder_repository.select(id=folder_id)
        if not folder:
            raise E([LOC_PATH, "folder_id"], folder_id,
                    ERR_VALUE_NOT_FOUND, status.HTTP_404_NOT_FOUND)

        elif folder.readonly:
            raise E([LOC_PATH, "folder_id"], folder_id,
                    ERR_VALUE_READONLY, status.HTTP_422_UNPROCESSABLE_CONTENT)

        # Check the file with the filename in the folder
        file_repository = Repository(session, cache, File, config)
        file = await file_repository.select(
            filename__eq=filename, folder_id__eq=folder_id)

        # Check the file with the filename in the directory
        file_path = File.path_for_filename(config, folder.name, filename)
        file_exists = await file_manager.isfile(file_path)

        # Inconsistent state: file exists but file does not
        if file and not file_exists:
            raise E([LOC_BODY, "file"], data.filename,
                    ERR_FILE_CONFLICT, status.HTTP_409_CONFLICT)

        # Inconsistent state: file exists but file does not
        elif not file and file_exists:
            raise E([LOC_BODY, "file"], data.filename,
                    ERR_FILE_CONFLICT, status.HTTP_409_CONFLICT)

        # Create a new file
        elif not file and not file_exists:
            await file_manager.upload(data, temporary_path)

            try:
                filesize, mimetype, checksum = (
                    await file_manager.filesize(temporary_path),
                    await file_manager.mimetype(temporary_path),
                    await file_manager.checksum(temporary_path))

                file = File(
                    current_user.id, folder.id, filename,
                    filesize, mimetype=mimetype, checksum=checksum)
                await file_repository.insert(file, commit=False)

                await file_manager.rename(temporary_path, file_path)
                file_renamed = True

                await file_repository.commit()
                lru.delete(file_path)

            except Exception:
                if file_renamed:
                    await file_manager.delete(file_path)
                else:
                    await file_manager.delete(temporary_path)
                raise

        # Update existing file and create revision
        elif file and file_exists:
            revision_path = None
            await file_manager.upload(data, temporary_path)

            # MIME type of an existing file must not be changed
            file_mimetype = await file_manager.mimetype(temporary_path)
            if file.mimetype != file_mimetype:
                await file_manager.delete(temporary_path)
                raise E([LOC_BODY, "file"], data.filename,
                        ERR_FILE_MIMETYPE_INVALID, status.HTTP_409_CONFLICT)

            # Check the file checksum
            try:
                file_checksum = await file_manager.checksum(temporary_path)
            except Exception:
                await file_manager.delete(temporary_path)
                raise

            # NOTE: File upload is idempotent: if file matches current
            # head (checksum), return successful response; skip DB/FS
            # changes, revision unchanged.

            if file.checksum != file_checksum:
                # Copy outdated file to revision
                revision_uuid = str(uuid.uuid4())
                revision_path = FileRevision.path_for_uuid(
                    config, revision_uuid)

                try:
                    await file_manager.copy(file_path, revision_path)
                except Exception:
                    await file_manager.delete(temporary_path)
                    raise

                # Outdated thumbnail will be removed after commit
                if file.has_thumbnail:
                    thumbnail_path = file.file_thumbnail.path(config)

                revision_repository = Repository(
                    session, cache, FileRevision, config)

                latest_revision_number = file.latest_revision_number + 1

                try:
                    # Create a new revision
                    revision = FileRevision(
                        current_user.id, file.id, latest_revision_number,
                        revision_uuid, file.filesize, file.checksum)
                    await revision_repository.insert(revision, commit=False)

                    # Update the file itself
                    file.latest_revision_number = latest_revision_number
                    file.file_thumbnail = None
                    file.checksum = file_checksum
                    file.filesize = await file_manager.filesize(
                        temporary_path)
                    await file_repository.update(file, commit=False)

                    # Atomic replacement of the file and commit
                    await file_manager.rename(temporary_path, file_path)
                    file_replaced = True

                    await file_repository.commit()
                    lru.delete(file_path)

                # Rollback if something goes wrong
                except Exception:
                    await file_repository.rollback()

                    try:
                        if file_replaced:
                            await file_manager.rename(revision_path, file_path)
                            revision_path = None
                        else:
                            await file_manager.delete(temporary_path)
                    except Exception:
                        pass  # nosec B110

                    if revision_path:
                        try:
                            await file_manager.delete(revision_path)
                        except Exception:
                            pass  # nosec B110

                    raise

            else:
                await file_manager.delete(temporary_path)

        # Remove the outdated thumbnail
        if thumbnail_path:
            try:
                await file_manager.delete(thumbnail_path)
                lru.delete(thumbnail_path)
            except Exception:
                pass  # nosec B110

        # Create a new thumbnail
        if ((file_renamed or file_replaced) and
                file.mimetype in IMAGE_MIMETYPES):
            thumbnail_uuid = str(uuid.uuid4())
            thumbnail_path = FileThumbnail.path_for_uuid(
                config, thumbnail_uuid)

            try:
                await file_manager.copy(file_path, thumbnail_path)
                await image_resize(
                    thumbnail_path, config.THUMBNAILS_WIDTH,
                    config.THUMBNAILS_HEIGHT, config.THUMBNAILS_QUALITY)

                thumbnail_repository = Repository(
                    session, cache, FileThumbnail, config)

                thumbnail_filesize, thumbnail_checksum = (
                    await file_manager.filesize(thumbnail_path),
                    await file_manager.checksum(thumbnail_path))

                thumbnail = FileThumbnail(
                    file.id, thumbnail_uuid, thumbnail_filesize,
                    thumbnail_checksum)

                await thumbnail_repository.insert(thumbnail)

            except Exception:
                await file_manager.delete(thumbnail_path)

    hook = Hook(request, session, cache, current_user=current_user)
    await hook.call(HOOK_AFTER_FILE_UPLOAD, file)

    return {
        "file_id": file.id,
        "latest_revision_number": file.latest_revision_number,
    }
