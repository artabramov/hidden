"""
The module defines a FastAPI router for retrieving the download list.
"""

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from app.database import get_session
from app.cache import get_cache
from app.decorators.locked_decorator import locked
from app.models.user_model import User, UserRole
from app.models.document_model import Document
from app.models.download_model import Download
from app.schemas.download_schemas import (
    DownloadListRequest, DownloadListResponse)
from app.repository import Repository
from app.hooks import Hook
from app.auth import auth
from app.constants import (
    HOOK_AFTER_DOWNLOAD_LIST, LOC_PATH, ERR_RESOURCE_NOT_FOUND)
from app.errors import E

router = APIRouter()


@router.get("/document/{document_id}/downloads",
            summary="Retrieve a list of document downloads.",
            response_class=JSONResponse, status_code=status.HTTP_200_OK,
            response_model=DownloadListResponse, tags=["Documents"])
@locked
async def document_downloads(
    document_id: int, schema=Depends(DownloadListRequest),
    session=Depends(get_session), cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.admin))
) -> DownloadListResponse:
    """
    Retrieve a list of document downloads. The router fetches the list
    of downloads from the repository based on the provided filter
    criteria, executes related hooks, and returns the results in a JSON
    response. The current user should have an admin role. Returns a 200
    response on success, a 401 error if authentication failed or the
    user does not have the required permissions, a 403 error if the
    token is missing, and a 423 error if the application is locked.

    **Args:**
    - `document_id`: The ID of the document for which downloads are
    being requested.
    - `DownloadListRequest`: The request schema containing the filters
    for the download list.

    **Returns:**
    - `DownloadListResponse`: A response schema containing the list of
    downloads and the total count of downloads.

    **Raises:**
    - `401 Unauthorized`: Raised if the token is invalid or expired,
    or if the current user is not authenticated or does not have the
    required permissions.
    - `403 Forbidden`: Raised if the token is missing.
    - `404 Not Found`: Raised if the document with the specified ID does
    not exist.
    - `422 Unprocessable Entity`: Raised if arguments validation failed.
    - `423 Locked`: Raised if the application is locked.

    **Auth:**
    - The user must provide a valid `JWT token` in the request header.
    - `admin` role is required to access this router.
    """
    document_repository = Repository(session, cache, Document)
    document = await document_repository.select(id=document_id)

    if not document:
        raise E([LOC_PATH, "document_id"], document_id,
                ERR_RESOURCE_NOT_FOUND, status.HTTP_404_NOT_FOUND)

    kwargs = schema.__dict__
    kwargs["document_id__eq"] = document_id

    download_repository = Repository(session, cache, Download)
    downloads = await download_repository.select_all(**kwargs)
    downloads_count = await download_repository.count_all(**kwargs)

    hook = Hook(session, cache, current_user=current_user)
    await hook.do(HOOK_AFTER_DOWNLOAD_LIST, downloads)

    return {
        "downloads": [await download.to_dict() for download in downloads],
        "downloads_count": downloads_count,
    }
