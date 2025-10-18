"""FastAPI router for folder deleting."""

from fastapi import APIRouter, Request, Depends, Path, status
from fastapi.responses import JSONResponse
from app.sqlite import get_session
from app.redis import get_cache
from app.models.user import User, UserRole
from app.models.folder import Folder
from app.models.file import File
from app.schemas.folder_delete import FolderDeleteResponse
from app.repository import Repository
from app.error import E, LOC_PATH, ERR_VALUE_NOT_FOUND
from app.hook import Hook, HOOK_AFTER_FOLDER_DELETE
from app.auth import auth

router = APIRouter()


@router.delete(
    "/folder/{folder_id}",
    status_code=status.HTTP_200_OK,
    response_class=JSONResponse,
    response_model=FolderDeleteResponse,
    summary="Delete folder",
    tags=["Folders"]
)
async def folder_delete(
    request: Request,
    folder_id: int = Path(..., ge=1),
    session=Depends(get_session),
    cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.admin))
) -> FolderDeleteResponse:
    """
    Delete a folder and all its files (including thumbnails, revisions,
    and head files).

    Disk cleanup is best-effort: missing thumbnails/revisions/head
    files are ignored. A WRITE lock on the folder is taken to block
    concurrent file operations during deletion.

    **Authentication:**
    - Requires a valid bearer token with `admin` role.

    **Path parameters:**
    - `folder_id` (integer ≥ 1): folder identifier.

    **Response:**
    - `FolderDeleteResponse` — returns the deleted folder ID.

    **Response codes:**
    - `200` — folder deleted.
    - `401` — missing, invalid, or expired token.
    - `403` — insufficient role, invalid JTI, user is inactive or
    suspended.
    - `404` — folder not found.
    - `423` — application is temporarily locked.
    - `498` — gocryptfs key is missing.
    - `499` — gocryptfs key is invalid.

    **Side effects:**
    - Removes thumbnails, revisions, and head files from the filesystem
    (best-effort); purges LRU cache entries.

    **Hooks:**
    - `HOOK_AFTER_FOLDER_DELETE` — executed after successful
    deletion.
    """
    config = request.app.state.config
    lru = request.app.state.lru
    file_manager = request.app.state.file_manager
    folder_locks = request.app.state.folder_locks

    # Ensure the folder exists
    folder_repository = Repository(session, cache, Folder, config)
    folder = await folder_repository.select(id=folder_id)

    if not folder:
        raise E([LOC_PATH, "folder_id"], folder_id,
                ERR_VALUE_NOT_FOUND, status.HTTP_404_NOT_FOUND)

    # NOTE: On folder delete, acquire the folder WRITE lock
    # to block any file operations inside.

    folder_lock = folder_locks[folder.id]
    async with folder_lock.write():

        # TODO: Switch to batched deletion (fixed-size chunks) to reduce
        # lock time and memory usage spikes during folder removal.

        file_repository = Repository(session, cache, File, config)
        files = await file_repository.select_all(
            folder_id__eq=folder.id)

        # NOTE: On folder delete, missing thumbnails/revisions/head
        # files are ignored; deletion proceeds without conflict errors
        # (best-effort cleanup).

        for file in files:

            # Remove the thumbnail file; no error if absent
            if file.has_thumbnail:
                thumbnail_path = file.file_thumbnail.path(config)
                await file_manager.delete(thumbnail_path)
                lru.delete(thumbnail_path)

            # Remove the revision files; no error if absent
            if file.has_revisions:
                for revision in file.file_revisions:
                    revision_path = revision.path(config)
                    await file_manager.delete(revision_path)
                    lru.delete(revision_path)

            # Remove the head file; no error if absent
            file_path = file.path(config)
            await file_manager.delete(file_path)
            lru.delete(file_path)

            # NOTE: On file delete, all related DB entities
            # are removed by SQLAlchemy using ORM relationships.

            await file_repository.delete(file)

        await folder_repository.delete(folder)

        folder_path = folder.path(config)
        await file_manager.rmdir(folder_path)

    hook = Hook(request, session, cache, current_user=current_user)
    await hook.call(HOOK_AFTER_FOLDER_DELETE, folder_id)

    return {"folder_id": folder.id}
