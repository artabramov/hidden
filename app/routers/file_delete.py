"""FastAPI router for file deleting."""

from fastapi import APIRouter, Depends, status, Request, Path
from fastapi.responses import JSONResponse
from app.sqlite import get_session
from app.redis import get_cache
from app.models.user import User, UserRole
from app.models.file import File
from app.schemas.file_delete import FileDeleteResponse
from app.hook import Hook, HOOK_AFTER_FILE_DELETE
from app.auth import auth
from app.repository import Repository
from app.error import (
    E, LOC_PATH, ERR_VALUE_NOT_FOUND, ERR_FILE_CONFLICT, ERR_VALUE_READONLY)

router = APIRouter()


@router.delete(
    "/file/{file_id}",
    status_code=status.HTTP_200_OK,
    response_class=JSONResponse,
    response_model=FileDeleteResponse,
    summary="Delete file",
    tags=["Files"]
)
async def file_delete(
    request: Request,
    file_id: int = Path(..., ge=1),
    session=Depends(get_session),
    cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.admin))
) -> FileDeleteResponse:
    """
    Delete a file and all associated artifacts (thumbnail, revisions,
    head file).

    **Authentication:**
    - Requires a valid bearer token with `admin` role.

    **Path parameters:**
    - `file_id` (integer ≥ 1): file identifier.

    **Response:**
    - `FileDeleteResponse` with file ID and latest revision
    number.

    **Response codes:**
    - `200` — file deleted successfully.
    - `401` — missing, invalid, or expired token.
    - `403` — insufficient role, invalid JTI, user is inactive or
    suspended.
    - `404` — file not found.
    - `409` — conflict: thumbnail, revision or head file is missing.
    - `423` — application is temporarily locked.
    - `498` — gocryptfs key is missing.
    - `499` — gocryptfs key is invalid.

    **Side effects:**
    - Deletes thumbnail, all revisions, and the head file from the
    filesystem; purges LRU cache entries.

    **Hooks:**
    - `HOOK_AFTER_FILE_DELETE` — executed after successful deletion.
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

    latest_revision_number = file.latest_revision_number

    # NOTE: On file delete, acquire the folder READ lock first,
    # then the per-file exclusive lock.

    folder_lock = folder_locks[file.folder_id]
    file_lock_key = (file.folder_id, file.filename)
    file_lock = file_locks[file_lock_key]
    async with folder_lock.read(), file_lock:

        # NOTE: On file delete the operation order is intentional:
        # (1) remove thumbnail, (2) remove revisions, (3) delete head.
        # The head is kept until the end to minimize the inconsistency
        # window. If filesystem operations fail, they likely fail at
        # step (1), so we fail early with minimal side effects. If any
        # step fails, the deletion is aborted entirely (no head removal).

        # Ensure the thumbnail file exists
        if file.has_thumbnail:
            thumbnail_path = file.file_thumbnail.path(config)
            thumbnail_file_exists = await file_manager.isfile(thumbnail_path)
            if not thumbnail_file_exists:
                raise E([LOC_PATH, "file_id"], file_id,
                        ERR_FILE_CONFLICT, status.HTTP_409_CONFLICT)

            await file_manager.delete(thumbnail_path)
            lru.delete(thumbnail_path)

        # Ensure the revision file exists
        if file.has_revisions:
            for revision in file.file_revisions:
                revision_path = revision.path(config)
                revision_file_exists = await file_manager.isfile(revision_path)
                if not revision_file_exists:
                    raise E([LOC_PATH, "file_id"], file_id,
                            ERR_FILE_CONFLICT, status.HTTP_409_CONFLICT)

                await file_manager.delete(revision_path)
                lru.delete(revision_path)

        # Ensure the head file exists
        file_path = file.path(config)
        current_file_exists = await file_manager.isfile(file_path)
        if not current_file_exists:
            raise E([LOC_PATH, "file_id"], file_id,
                    ERR_FILE_CONFLICT, status.HTTP_409_CONFLICT)

        await file_manager.delete(file_path)
        lru.delete(file_path)

        # NOTE: On file delete, all related DB entities
        # are removed by SQLAlchemy using ORM relationships.

        await file_repository.delete(file)

    hook = Hook(request, session, cache, current_user=current_user)
    await hook.call(HOOK_AFTER_FILE_DELETE, file_id)

    return {
        "file_id": file_id,
        "latest_revision_number": latest_revision_number,
    }
