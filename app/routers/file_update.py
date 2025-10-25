"""FastAPI router for file changing."""

from fastapi import APIRouter, Request, Depends, Path, status
from fastapi.responses import JSONResponse
from app.sqlite import get_session
from app.redis import get_cache
from app.models.user import User, UserRole
from app.models.file import File
from app.models.folder import Folder
from app.schemas.file_update import (
    FileUpdateRequest, FileUpdateResponse)
from app.validators.file_validators import name_validate
from app.hook import Hook, HOOK_AFTER_FILE_UPDATE
from app.auth import auth
from app.repository import Repository
from app.error import (
    E, LOC_PATH, LOC_BODY, ERR_VALUE_NOT_FOUND, ERR_VALUE_INVALID,
    ERR_FILE_CONFLICT, ERR_VALUE_READONLY)

router = APIRouter()


@router.put(
    "/file/{file_id}",
    status_code=status.HTTP_200_OK,
    response_class=JSONResponse,
    response_model=FileUpdateResponse,
    summary="Update file",
    tags=["Files"]
)
async def file_update(
    request: Request,
    schema: FileUpdateRequest,
    file_id: int = Path(..., ge=1),
    session=Depends(get_session),
    cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.editor))
) -> FileUpdateResponse:
    """
    Updates a file by renaming its head file, moving the head file to
    a different folder (keeping its name), and/or changing the file
    summary. Disk changes are performed with an atomic rename; the file
    row is staged (no-commit), the file is renamed or moved on disk, and
    then the transaction is committed to keep database and filesystem in
    sync.

    Concurrency is controlled with per-path locks. For rename/move, two
    locks are acquired in a deterministic order to prevent deadlocks.
    All database and filesystem checks are executed inside this critical
    section. These locks are in-process.

    Files are stored under their folder directory. The database enforces
    uniqueness of (folder_id, filename) for files.

    **Authentication:**
    - Requires a valid bearer token with `editor` role or higher.

    **Validation schemas:**
    - `FileUpdateRequest` — optional fields: `filename`, `summary`,
    `folder_id`.
    - `FileUpdateResponse` — returns `file_id` and
    `latest_revision_number`.

    **Path parameters:**
    - `file_id` (integer ≥ 1) — file identifier.

    **Request body:**
    - `application/json` with any of: `filename`, `summary`,
    `folder_id`.

    **Response codes:**
    - `200` — update successful.
    - `401` — missing, invalid, or expired token.
    - `403` — insufficient role, invalid JTI, user is inactive or
    suspended.
    - `404` — file not found.
    - `409` — conflict: name already exists in DB/FS or DB/FS mismatch
    (file present but file missing, or vice versa).
    - `422` — invalid file name.
    - `423` — application is temporarily locked.
    - `498` — gocryptfs key is missing.
    - `499` — gocryptfs key is invalid.

    **Hooks:**
    - `HOOK_AFTER_FILE_UPDATE` — executed after a successful update.
    """
    config = request.app.state.config
    file_manager = request.app.state.file_manager
    lru = request.app.state.lru

    folder_locks = request.app.state.folder_locks
    file_locks = request.app.state.file_locks

    file_repository = Repository(session, cache, File, config)
    file = await file_repository.select(id=file_id)

    if not file:
        raise E([LOC_PATH, "file_id"], file_id,
                ERR_VALUE_NOT_FOUND, status.HTTP_404_NOT_FOUND)

    elif file.file_folder.readonly:
        raise E([LOC_PATH, "file_id"], file.folder_id,
                ERR_VALUE_READONLY, status.HTTP_422_UNPROCESSABLE_CONTENT)

    file.summary = schema.summary
    file_updated = False

    # Checking the correctness of the file name
    try:
        filename = name_validate(schema.filename)
    except ValueError:
        raise E([LOC_BODY, "file"], schema.filename, ERR_VALUE_INVALID,
                status.HTTP_422_UNPROCESSABLE_ENTITY)

    # NOTE: On file update, a small TOCTOU window remains; for
    # strict guarantees, revalidate entities under the locks right
    # before rename/move.

    # Rename the file if the filename changes
    if file.filename != filename:

        # NOTE: On file rename, acquire the folder READ lock first,
        # then the per-file exclusive lock.

        folder_lock = folder_locks[file.folder_id]

        first_lock_key = (file.folder_id, file.filename)
        second_lock_key = (file.folder_id, filename)

        first_lock_key, second_lock_key = sorted((
            first_lock_key, second_lock_key))

        first_file_lock = file_locks[first_lock_key]
        second_file_lock = file_locks[second_lock_key]

        async with folder_lock.read(), first_file_lock, second_file_lock:

            # Check the file with the filename in the folder
            filename_exists = await file_repository.select(
                id__ne=file.id, filename__eq=filename,
                folder_id__eq=file.folder_id)
            if filename_exists:
                raise E([LOC_BODY, "file"], filename,
                        ERR_FILE_CONFLICT, status.HTTP_409_CONFLICT)

            # Check the file with the current filename in the directory
            current_file_path = file.path(config)
            current_file_exists = await file_manager.isfile(current_file_path)
            if not current_file_exists:
                raise E([LOC_BODY, "file"], file.filename,
                        ERR_FILE_CONFLICT, status.HTTP_409_CONFLICT)

            # Check the file with the new filename in the directory
            updated_file_path = File.path_for_filename(
                config, file.file_folder.name, filename)
            updated_file_exists = await file_manager.isfile(updated_file_path)
            if updated_file_exists:
                raise E([LOC_BODY, "file"], filename,
                        ERR_FILE_CONFLICT, status.HTTP_409_CONFLICT)

            try:
                file.filename = filename
                await file_repository.update(file, commit=False)
                await file_manager.rename(current_file_path, updated_file_path)
                lru.delete(current_file_path)
                lru.delete(updated_file_path)

                await file_repository.commit()
                file_updated = True

            except Exception:
                await file_repository.rollback()
                raise

    # Move the file if folder changes
    if file.folder_id != schema.folder_id:
        folder_repository = Repository(session, cache, Folder, config)

        # Does the target folder exist?
        target_folder = await folder_repository.select(id=schema.folder_id)
        if not target_folder:
            raise E([LOC_BODY, "folder_id"], schema.folder_id,
                    ERR_VALUE_NOT_FOUND, status.HTTP_404_NOT_FOUND)

        # NOTE: On file move, acquire READ locks on both folders
        # first, then the per-file exclusive lock on both file paths;

        cid_a, cid_b = sorted([file.folder_id, schema.folder_id])
        folder_lock_a = folder_locks[cid_a]
        folder_lock_b = folder_locks[cid_b]

        async with folder_lock_a.read(), folder_lock_b.read():
            first_lock_key = (file.folder_id, file.filename)
            second_lock_key = (schema.folder_id, file.filename)

            first_lock_key, second_lock_key = sorted((
                first_lock_key, second_lock_key))

            first_file_lock = file_locks[first_lock_key]
            second_file_lock = file_locks[second_lock_key]

            async with first_file_lock, second_file_lock:

                # Does the filename exist in the target folder?
                filename_exists = await file_repository.select(
                    folder_id__eq=schema.folder_id, filename__eq=file.filename)
                if filename_exists:
                    raise E([LOC_BODY, "file"], file.filename,
                            ERR_FILE_CONFLICT, status.HTTP_409_CONFLICT)

                # Is there a file in the current directory?
                current_file_path = file.path(config)
                current_file_exists = await file_manager.isfile(
                    current_file_path)
                if not current_file_exists:
                    raise E([LOC_BODY, "file"], file.filename,
                            ERR_FILE_CONFLICT, status.HTTP_409_CONFLICT)

                # Is there a file in the target directory?
                target_file_path = File.path_for_filename(
                    config, target_folder.name, file.filename)
                target_file_exists = await file_manager.isfile(
                    target_file_path)

                if target_file_exists:
                    raise E([LOC_BODY, "file"], file.filename,
                            ERR_FILE_CONFLICT, status.HTTP_409_CONFLICT)

                try:
                    file.folder_id = target_folder.id
                    await file_repository.update(file, commit=False)
                    await file_manager.rename(
                        current_file_path, target_file_path)
                    lru.delete(current_file_path)
                    lru.delete(target_file_path)

                    await file_repository.commit()
                    file_updated = True

                except Exception:
                    await file_repository.rollback()
                    raise

    if not file_updated:
        await file_repository.update(file)

    hook = Hook(request, session, cache, current_user=current_user)
    await hook.call(HOOK_AFTER_FILE_UPDATE, file)

    return {
        "file_id": file.id,
        "latest_revision_number": file.latest_revision_number,
    }
