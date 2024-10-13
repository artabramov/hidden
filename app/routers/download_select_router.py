"""
The module defines a FastAPI router for retrieving download entities.
"""

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from app.database import get_session
from app.cache import get_cache
from app.decorators.locked_decorator import locked
from app.models.user_model import User, UserRole
from app.models.download_model import Download
from app.schemas.download_schemas import DownloadSelectResponse
from app.repository import Repository
from app.errors import E
from app.hooks import Hook
from app.auth import auth
from app.constants import (
    LOC_PATH, ERR_RESOURCE_NOT_FOUND, HOOK_AFTER_DOWNLOAD_SELECT)

router = APIRouter()


@router.get("/document/{document_id}/download/{download_id}",
            summary="Retrieve download",
            response_class=JSONResponse, status_code=status.HTTP_200_OK,
            response_model=DownloadSelectResponse, tags=["Documents"])
@locked
async def download_select(
    document_id: int, download_id: int,
    session=Depends(get_session), cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.admin))
) -> DownloadSelectResponse:
    """
    FastAPI router for retrieving a download entity. The router fetches
    the download from the repository using the provided ID, executes
    related hooks, and returns the download details in a JSON response.
    The current user should have an admin role. Returns a 200 response
    on success, a 404 error if the download is not found, and a 403
    error if authentication fails or the user does not have the
    required role.
    """
    download_repository = Repository(session, cache, Download)
    download = await download_repository.select(id=download_id)

    if not download or download.document_id != document_id:
        raise E([LOC_PATH, "download_id"], download_id,
                ERR_RESOURCE_NOT_FOUND, status.HTTP_404_NOT_FOUND)

    hook = Hook(session, cache, current_user=current_user)
    await hook.do(HOOK_AFTER_DOWNLOAD_SELECT, download)

    return download.to_dict()
