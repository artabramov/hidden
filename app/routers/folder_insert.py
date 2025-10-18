"""FastAPI router for creating folders."""

import os
from fastapi import APIRouter, Depends, status, Request
from fastapi.responses import JSONResponse
from app.sqlite import get_session
from app.redis import get_cache
from app.models.folder import Folder
from app.models.user import User, UserRole
from app.repository import Repository
from app.schemas.folder_insert import FolderInsertRequest, FolderInsertResponse
from app.hook import Hook, HOOK_AFTER_FOLDER_INSERT
from app.error import E, LOC_BODY, ERR_VALUE_EXISTS
from app.auth import auth

router = APIRouter()


@router.post("/folder", summary="Create new folder.",
             response_class=JSONResponse, status_code=status.HTTP_201_CREATED,
             response_model=FolderInsertResponse, tags=["Folders"])
async def folder_insert(
    request: Request, schema: FolderInsertRequest,
    session=Depends(get_session), cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.writer))
) -> FolderInsertResponse:
    """
    Create a new folder and a matching directory on the filesystem, then
    return the ID. The folder name must be unique; if a name is already
    taken, the request is rejected.

    **Authentication:**
    - Requires a valid bearer token with `writer` role or higher.

    **Validation schemas:**
    - `FolderInsertRequest` — request body with read-only flag,
    name, and optional summary.
    - `FolderInsertResponse` — contains the newly created folder ID.

    **Request body:**
    - `readonly` (boolean): read-only flag for the folder.
    - `name` (string, 1-256; ≤255 UTF-8 bytes): folder name;
    trimmed; `/` and NUL are not allowed.
    - `summary` (string, 0-4096): optional description; trimmed; empty
    becomes NULL.

    **Response codes:**
    - `201` — folder successfully created.
    - `401` — missing, invalid, or expired token.
    - `403` — insufficient role, invalid JTI, user is inactive or
    suspended.
    - `422` — name already exists or fails validation.
    - `423` — application is temporarily locked.
    - `498` — gocryptfs key is missing.
    - `499` — gocryptfs key is invalid.

    **Side effects:**
    - Creates a directory at `files/<name>`.

    **Hooks:**
    - `HOOK_AFTER_FOLDER_INSERT`: executed after folder and directory
    are successfully created.
    """
    config = request.app.state.config
    file_manager = request.app.state.file_manager
    folder_repository = Repository(session, cache, Folder, config)

    folder_exists = await folder_repository.exists(
        name__eq=schema.name)

    if folder_exists:
        raise E([LOC_BODY, "name"], schema.name,
                ERR_VALUE_EXISTS, status.HTTP_422_UNPROCESSABLE_ENTITY)

    folder_path = os.path.join(config.FILES_DIR, schema.name)
    await file_manager.mkdir(folder_path)

    folder = Folder(
        current_user.id, schema.readonly, schema.name, summary=schema.summary)
    await folder_repository.insert(folder)

    hook = Hook(request, session, cache, current_user=current_user)
    await hook.call(HOOK_AFTER_FOLDER_INSERT, folder)

    # TODO: remove redundant logging
    request.state.log.debug(
        "folder created; folder_id=%s;", folder.id)
    return {"folder_id": folder.id}
