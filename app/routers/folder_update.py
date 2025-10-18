from fastapi import APIRouter, Request, Depends, Path, status
from fastapi.responses import JSONResponse
from app.sqlite import get_session
from app.redis import get_cache
from app.models.user import User, UserRole
from app.models.folder import Folder
from app.schemas.folder_update import FolderUpdateRequest, FolderUpdateResponse
from app.repository import Repository
from app.error import (
    E, LOC_PATH, LOC_BODY, ERR_VALUE_NOT_FOUND, ERR_VALUE_EXISTS)
from app.hook import Hook, HOOK_AFTER_FOLDER_UPDATE
from app.auth import auth

router = APIRouter()


@router.put(
    "/folder/{folder_id}",
    status_code=status.HTTP_200_OK,
    response_class=JSONResponse,
    response_model=FolderUpdateResponse,
    summary="Update folder",
    tags=["Folders"]
)
async def folder_update(
    request: Request,
    schema: FolderUpdateRequest,
    folder_id: int = Path(..., ge=1),
    session=Depends(get_session),
    cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.editor))
) -> FolderUpdateResponse:
    """
    Updates a folder's properties and, if the name changes, renames
    the underlying directory on disk. The operation updates: name,
    readonly status, and summary. Changes are performed under an
    exclusive folder lock to keep the database and filesystem in
    sync. folder names are unique across the application; both the
    database and the filesystem are validated before applying changes.

    **Authentication:**
    - Requires a valid bearer token with `editor` role or higher.

    **Validation schemas:**
    - `FolderUpdateRequest` — optional fields: `name`, `readonly`,
      `summary`.
    - `FolderUpdateResponse` — returns `folder_id`.

    **Path parameters:**
    - `folder_id` (integer ≥ 1) — folder identifier.

    **Request body:**
    - `application/json` with any of: `name`, `readonly`, `summary`.

    **Response codes:**
    - `200` — update successful.
    - `401` — missing, invalid, or expired token.
    - `403` — insufficient role, invalid JTI, user is inactive or
      suspended.
    - `404` — folder not found.
    - `422` — validation error (e.g., `name` already exists).
    - `423` — application is temporarily locked.
    - `498` — gocryptfs key is missing.
    - `499` — gocryptfs key is invalid.

    **Locks & consistency:**
    - Exclusive per-folder lock during the update.
    - On rename, directory existence is checked before moving; any
    failure triggers a best-effort rollback of the directory move.

    **Hooks:**
    - `HOOK_AFTER_FOLDER_UPDATE` — executed after a successful
    update.
    """
    config = request.app.state.config
    file_manager = request.app.state.file_manager
    log = request.state.log

    folder_repository = Repository(session, cache, Folder, config)
    folder = await folder_repository.select(id=folder_id)

    if not folder:
        raise E([LOC_PATH, "folder_id"], folder_id,
                ERR_VALUE_NOT_FOUND, status.HTTP_404_NOT_FOUND)

    # Does a folder with this name already exist?
    folder_exists = await folder_repository.exists(
        name__eq=schema.name, id__ne=folder.id)

    if folder_exists:
        raise E([LOC_BODY, "name"], schema.name,
                ERR_VALUE_EXISTS, status.HTTP_422_UNPROCESSABLE_ENTITY)

    current_name = folder.name
    current_path = folder.path(config)

    updated_name = schema.name
    updated_path = Folder.path_for_dir(config, updated_name)

    # Exclusive lock on the folder
    folder_lock = request.app.state.folder_locks[folder.id]
    async with folder_lock.write():

        # No-op rename
        if updated_name == current_name:
            folder.readonly = schema.readonly
            folder.summary = schema.summary
            await folder_repository.update(folder)

        else:
            # Does a directory with this name already exist?
            directory_exists = await file_manager.isdir(updated_path)
            if directory_exists:
                raise E([LOC_BODY, "name"], schema.name,
                        ERR_VALUE_EXISTS, status.HTTP_422_UNPROCESSABLE_ENTITY)

            try:
                folder_renamed = False
                await file_manager.rename(current_path, updated_path)
                folder_renamed = True

                folder.name = schema.name
                folder.readonly = schema.readonly
                folder.summary = schema.summary
                await folder_repository.update(folder)

            except Exception:
                if folder_renamed:
                    try:
                        await file_manager.rename(updated_path, current_path)

                    except Exception:
                        log.exception(
                            "folder rename failed; folder_id=%s;",
                            folder.id)

                # Rollback successful: raise original
                # error without losing stacktrace
                raise

    hook = Hook(request, session, cache, current_user=current_user)
    await hook.call(HOOK_AFTER_FOLDER_UPDATE, folder)

    log.debug("folder updated; folder_id=%s;", folder.id)
    return {"folder_id": folder.id}
