"""FastAPI router for retrieving folder details by ID."""

from fastapi import APIRouter, Depends, status, Request, Path
from fastapi.responses import JSONResponse
from app.sqlite import get_session
from app.redis import get_cache
from app.models.user import User, UserRole
from app.models.folder import Folder
from app.schemas.folder_select import FolderSelectResponse
from app.repository import Repository
from app.error import E, LOC_PATH, ERR_VALUE_NOT_FOUND
from app.hook import Hook, HOOK_AFTER_FOLDER_SELECT
from app.auth import auth

router = APIRouter()


@router.get(
    "/folder/{folder_id}",
    status_code=status.HTTP_200_OK,
    response_class=JSONResponse,
    response_model=FolderSelectResponse,
    tags=["Folders"],
    summary="Retrieve folder",
)
async def folder_select(
    request: Request,
    folder_id: int = Path(..., ge=1),
    session=Depends(get_session),
    cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.reader)),
) -> FolderSelectResponse:
    """
    Retrieve a single folder by ID and return its details, including
    creator info, creation and updateion timestamps, read-only flag,
    name, and optional summary.

    **Authentication:**
    - Requires a valid bearer token with `reader` role or higher.

    **Response schema:**
    - `FolderSelectResponse` — includes folder ID; creator;
    creation and last-update timestamps (Unix seconds, UTC); read-only
    flag; normalized name; and optional summary.

    **Path parameters:**
    - `folder_id` (integer): identifier of the folder to retrieve.

    **Response codes:**
    - `200` — folder found; details returned.
    - `401` — missing, invalid, or expired token.
    - `403` — insufficient role, invalid JTI, user is inactive or
    suspended.
    - `404` — folder not found.
    - `423` — application is temporarily locked.
    - `498` — gocryptfs key is missing.
    - `499` — gocryptfs key is invalid.

    **Hooks:**
    - `HOOK_AFTER_FOLDER_SELECT`: executed after a successful
    retrieval.
    """

    config = request.app.state.config

    folder_repository = Repository(session, cache, Folder, config)
    folder = await folder_repository.select(id=folder_id)

    if not folder:
        raise E([LOC_PATH, "folder_id"], folder_id,
                ERR_VALUE_NOT_FOUND, status.HTTP_404_NOT_FOUND)

    hook = Hook(request, session, cache, current_user=current_user)
    await hook.call(HOOK_AFTER_FOLDER_SELECT, folder)

    return await folder.to_dict()
