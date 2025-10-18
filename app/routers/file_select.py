"""FastAPI router for file retrieving."""

from fastapi import APIRouter, Depends, status, Request, Path
from fastapi.responses import JSONResponse
from app.sqlite import get_session
from app.redis import get_cache
from app.models.user import User, UserRole
from app.models.folder import Folder
from app.models.file import File
from app.schemas.file_select import FileSelectResponse
from app.hook import Hook, HOOK_AFTER_FILE_SELECT
from app.auth import auth
from app.repository import Repository
from app.error import E, LOC_PATH, ERR_VALUE_NOT_FOUND

router = APIRouter()


@router.get(
    "/folder/{folder_id}/file/{file_id}",
    status_code=status.HTTP_200_OK,
    response_class=JSONResponse,
    response_model=FileSelectResponse,
    summary="Retrieve file",
    tags=["Files"]
)
async def file_select(
    request: Request,
    folder_id: int = Path(..., ge=1),
    file_id: int = Path(..., ge=1),
    session=Depends(get_session),
    cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.reader))
) -> FileSelectResponse:
    """
    Retrieve a single file by ID within a given folder and return its
    details, including creator, parent folder, timestamps, flagged
    status, filename, size, MIME type, checksum, summary, and latest
    revision.

    **Authentication:**
    - Requires a valid bearer token with `reader` role or higher.

    **Response schema:**
    - `FileSelectResponse` — includes file ID; creator; parent folder;
    creation and last-update timestamps (Unix seconds, UTC); flagged
    status; filename; file size; MIME type (optional); content checksum;
    optional summary; and the latest revision number.

    **Path parameters:**
    - `folder_id` (integer ≥ 1): parent folder identifier.
    - `file_id` (integer ≥ 1): file identifier.

    **Response codes:**
    - `200` — file found; details returned.
    - `401` — missing, invalid, or expired token.
    - `403` — insufficient role, invalid JTI, user is inactive or
    suspended.
    - `404` — folder or file not found.
    - `423` — application is temporarily locked.
    - `498` — gocryptfs key is missing.
    - `499` — gocryptfs key is invalid.

    **Hooks:**
    - `HOOK_AFTER_FILE_SELECT`: executed after a successful
    retrieval.
    """
    config = request.app.state.config

    # NOTE: On file select, keep two-step fetch to hit Redis cache;
    # load the folder by ID first, then load the file by ID.

    folder_repository = Repository(session, cache, Folder, config)
    folder = await folder_repository.select(id=folder_id)

    if not folder:
        raise E([LOC_PATH, "folder_id"], folder_id,
                ERR_VALUE_NOT_FOUND, status.HTTP_404_NOT_FOUND)

    file_repository = Repository(session, cache, File, config)
    file = await file_repository.select(id=file_id)

    if not file or file.folder_id != folder.id:
        raise E([LOC_PATH, "file_id"], file_id,
                ERR_VALUE_NOT_FOUND, status.HTTP_404_NOT_FOUND)

    hook = Hook(request, session, cache, current_user=current_user)
    await hook.call(HOOK_AFTER_FILE_SELECT, file)

    return await file.to_dict()
