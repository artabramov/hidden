"""FastAPI router for file changing."""

from fastapi import APIRouter, Request, Depends, Path, status
from fastapi.responses import JSONResponse
from app.sqlite import get_session
from app.redis import get_cache
from app.models.user import User, UserRole
from app.models.collection import Collection
from app.models.file import File
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
    "/collection/{collection_id}/file/{file_id}",
    status_code=status.HTTP_200_OK,
    response_class=JSONResponse,
    response_model=FileUpdateResponse,
    summary="Update file",
    tags=["Files"]
)
async def file_update(
    request: Request,
    schema: FileUpdateRequest,
    collection_id: int = Path(..., ge=1),
    file_id: int = Path(..., ge=1),
    session=Depends(get_session),
    cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.editor))
) -> FileUpdateResponse:
    """
    Updates a file by renaming its head file within the current
    collection, moving the head file to a different collection (keeping
    its name), and/or changing the file summary. Disk changes are
    performed with an atomic rename; the file row is staged
    (no-commit), the file is renamed or moved on disk, and then the
    transaction is committed to keep database and filesystem in sync.

    Concurrency is controlled with per-path locks. For rename/move, two
    locks are acquired in a deterministic order to prevent deadlocks.
    All database and filesystem checks are executed inside this critical
    section. These locks are in-process.

    Files are stored under their collection directory. The database
    enforces uniqueness of (collection_id, filename) for files.

    **Authentication:**
    - Requires a valid bearer token with `editor` role or higher.

    **Validation schemas:**
    - `FileUpdateRequest` — optional fields: `filename`, `summary`,
    `collection_id`.
    - `FileUpdateResponse` — returns `file_id` and
    `latest_revision_number`.

    **Path parameters:**
    - `collection_id` (integer ≥ 1) — current collection identifier.
    - `file_id` (integer ≥ 1) — file identifier.

    **Request body:**
    - `application/json` with any of: `filename`, `summary`,
    `collection_id`.

    **Response codes:**
    - `200` — update successful.
    - `401` — missing, invalid, or expired token.
    - `403` — insufficient role, invalid JTI, user is inactive or
    suspended.
    - `404` — collection or file not found.
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

    collection_locks = request.app.state.collection_locks
    file_locks = request.app.state.file_locks

    # NOTE: On file update, keep two-step fetch to hit Redis cache;
    # load the collection by ID first, then load the file by ID.

    collection_repository = Repository(session, cache, Collection, config)
    collection = await collection_repository.select(id=collection_id)

    if not collection:
        raise E([LOC_PATH, "collection_id"], collection_id,
                ERR_VALUE_NOT_FOUND, status.HTTP_404_NOT_FOUND)

    elif collection.readonly:
        raise E([LOC_PATH, "collection_id"], collection_id,
                ERR_VALUE_READONLY, status.HTTP_422_UNPROCESSABLE_CONTENT)

    file_repository = Repository(session, cache, File, config)
    file = await file_repository.select(id=file_id)

    if not file or file.collection_id != collection.id:
        raise E([LOC_PATH, "file_id"], file_id,
                ERR_VALUE_NOT_FOUND, status.HTTP_404_NOT_FOUND)

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

        # NOTE: On file rename, acquire the collection READ lock first,
        # then the per-file exclusive lock.

        collection_lock = collection_locks[collection_id]

        first_lock_key = (collection_id, file.filename)
        second_lock_key = (collection_id, filename)

        first_lock_key, second_lock_key = sorted((
            first_lock_key, second_lock_key))

        first_file_lock = file_locks[first_lock_key]
        second_file_lock = file_locks[second_lock_key]

        async with collection_lock.read(), first_file_lock, second_file_lock:

            # Check the file with the filename in the collection
            filename_exists = await file_repository.select(
                id__ne=file.id, filename__eq=filename,
                collection_id__eq=collection.id)
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
                config, collection.name, filename)
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

    # Move the file if collection changes
    if file.collection_id != schema.collection_id:

        # Does the target collection exist?
        target_collection = await collection_repository.select(
            id=schema.collection_id)
        if not target_collection:
            raise E([LOC_BODY, "collection_id"], schema.collection_id,
                    ERR_VALUE_NOT_FOUND, status.HTTP_404_NOT_FOUND)

        # NOTE: On file move, acquire READ locks on both collections
        # first, then the per-file exclusive lock on both file paths;

        cid_a, cid_b = sorted([file.collection_id, schema.collection_id])
        collection_lock_a = collection_locks[cid_a]
        collection_lock_b = collection_locks[cid_b]

        async with collection_lock_a.read(), collection_lock_b.read():
            first_lock_key = (collection_id, file.filename)
            second_lock_key = (schema.collection_id, file.filename)

            first_lock_key, second_lock_key = sorted((
                first_lock_key, second_lock_key))

            first_file_lock = file_locks[first_lock_key]
            second_file_lock = file_locks[second_lock_key]

            async with first_file_lock, second_file_lock:

                # Does the filename exist in the target collection?
                filename_exists = await file_repository.select(
                    collection_id__eq=schema.collection_id,
                    filename__eq=file.filename)
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
                    config, target_collection.name, file.filename)
                target_file_exists = await file_manager.isfile(
                    target_file_path)

                if target_file_exists:
                    raise E([LOC_BODY, "file"], file.filename,
                            ERR_FILE_CONFLICT, status.HTTP_409_CONFLICT)

                try:
                    file.collection_id = target_collection.id
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
