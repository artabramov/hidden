"""FastAPI router for folder listing."""

from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import JSONResponse
from app.sqlite import get_session
from app.redis import get_cache
from app.models.user import User, UserRole
from app.models.folder import Folder
from app.schemas.folder_list import FolderListRequest, FolderListResponse
from app.hook import Hook, HOOK_AFTER_FOLDER_LIST
from app.auth import auth
from app.repository import Repository

router = APIRouter()


@router.get(
    "/folders",
    status_code=status.HTTP_200_OK,
    response_class=JSONResponse,
    response_model=FolderListResponse,
    summary="Retrieve list of folders",
    tags=["Folders"]
)
async def folder_list(
    request: Request,
    schema=Depends(FolderListRequest),
    session=Depends(get_session), cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.reader))
) -> FolderListResponse:
    """
    Retrieve folders matching the provided filters and return them with
    the total number of matches.

    **Authentication**
    - Requires a valid bearer token with `reader` role or higher.

    **Query parameters**
    - `FolderListRequest` — optional filters (creation time, creator,
    readonly flag, name), pagination (offset/limit), and ordering
    (order_by/order).

    **Response**
    - `FolderListResponse` — page of folders and total match
    count.

    **Response codes**
    - `200` — folder list returned.
    - `401` — missing, invalid, or expired token.
    - `403` — insufficient role, invalid JTI, user is inactive or
    suspended.
    - `423` — application is temporarily locked.
    - `498` — gocryptfs key is missing.
    - `499` — gocryptfs key is invalid.

    **Hooks**
    - `HOOK_AFTER_FOLDER_LIST` — executed after successful retrieval.
    """
    config = request.app.state.config
    kwargs = schema.model_dump(exclude_none=True)

    folder_repository = Repository(session, cache, Folder, config)
    folders = await folder_repository.select_all(**kwargs)
    folders_count = await folder_repository.count_all(**kwargs)

    hook = Hook(request, session, cache, current_user=current_user)
    await hook.call(HOOK_AFTER_FOLDER_LIST, folders, folders_count)

    return {
        "folders": [await folder.to_dict() for folder in folders],
        "folders_count": folders_count,
    }
