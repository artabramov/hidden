"""FastAPI router for file listing."""

from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import JSONResponse
from app.sqlite import get_session
from app.redis import get_cache
from app.managers.entity_manager import SUBQUERY
from app.models.user import User, UserRole
from app.models.file import File
from app.models.file_tag import FileTag
from app.schemas.file_list import FileListRequest, FileListResponse
from app.hook import Hook, HOOK_AFTER_FILE_LIST
from app.auth import auth
from app.repository import Repository

router = APIRouter()


@router.get(
    "/files",
    status_code=status.HTTP_200_OK,
    response_class=JSONResponse,
    response_model=FileListResponse,
    summary="Retrieve list of files",
    tags=["Files"]
)
async def file_list(
    request: Request,
    schema=Depends(FileListRequest),
    session=Depends(get_session), cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.reader))
) -> FileListResponse:
    """
    Retrieve files matching the provided filters and return them
    with the total number of matches.

    **Authentication:**
    - Requires a valid bearer token with `reader` role or higher.

    **Query parameters:**
    - `FileListRequest` — optional filters (folder_id, creation time,
    creator, flagged status, filename/mimetype, file size), pagination
    (offset and limit), and ordering (order_by and order).

    **Response:**
    - `FileListResponse` — page of files and total match count.

    **Response codes:**
    - `200` — list returned.
    - `401` — missing, invalid, or expired token.
    - `403` — insufficient role, invalid JTI, user is inactive or
    suspended.
    - `423` — application is temporarily locked.
    - `498` — gocryptfs key is missing.
    - `499` — gocryptfs key is invalid.

    **Hooks:**
    - `HOOK_AFTER_FILE_LIST`: executed after successful retrieval.
    """
    config = request.app.state.config
    kwargs = schema.model_dump(exclude_none=True)

    file_repository = Repository(session, cache, File, config)

    if schema.tag_value__eq is not None:
        kwargs[SUBQUERY] = await file_repository.entity_manager.subquery(
            FileTag, "file_id", value__eq=schema.tag_value__eq)

    files = await file_repository.select_all(**kwargs)
    files_count = await file_repository.count_all(**kwargs)

    hook = Hook(request, session, cache, current_user=current_user)
    await hook.call(HOOK_AFTER_FILE_LIST, files, files_count)

    return {
        "files": [await file.to_dict() for file in files],
        "files_count": files_count,
    }
