import os
from fastapi import APIRouter, Depends, status, Response
from fastapi.responses import JSONResponse
from app.postgres import get_session
from app.redis import get_cache
from app.models.user_model import User, UserRole
from app.mixins.meta_mixin import META_DOWNLOADS_COUNT
from app.error import E, LOC_PATH, ERR_FILE_NOT_FOUND
from app.auth import auth
from app.config import get_config
from app.lru import LRU
from app.helpers.encrypt_helper import hash_str
from app.repository import Repository
from app.models.document_model import Document

cfg = get_config()
lru = LRU(cfg.DOCUMENTS_LRU_SIZE)
router = APIRouter()


@router.get("/documents/{document_filename}", summary="Download a document.",
            response_class=JSONResponse, status_code=status.HTTP_200_OK,
            tags=["Files"])
async def document_download(
    document_filename: str,
    session=Depends(get_session), cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.reader))
) -> Response:
    """
    Download a document. Loads the original file by its filename from
    disk (using an LRU cache), and returns the file in the response with
    appropriate headers.

    **Auth:**
    - The token must be included in the request header and contain auth
    data for an active user with the `reader`, `writer`, `editor`, or
    `admin` role.

    **Returns:**
    - `Response`: File content on success.

    **Responses:**
    - `200 OK`: If the file is successfully returned.
    - `401 Unauthorized`: If the token is invalid or lacks permissions.
    - `403 Forbidden`: If the token or secret key is missing.
    - `404 Not Found`: If the file is not found.
    - `423 Locked`: If the app is locked.
    """
    document_path = os.path.join(cfg.DOCUMENTS_PATH, document_filename)
    document_data = await lru.load(document_path)

    if not document_data:
        raise E([LOC_PATH, "document_filename"], document_filename,
                ERR_FILE_NOT_FOUND, status.HTTP_404_NOT_FOUND)

    document_filename_hash = hash_str(document_filename)
    document_repository = Repository(session, cache, Document)
    document = await document_repository.select(
        document_filename_hash__eq=document_filename_hash)

    if not document:
        raise E([LOC_PATH, "document_filename"], document_filename,
                ERR_FILE_NOT_FOUND, status.HTTP_404_NOT_FOUND)

    await document_repository.update(document)

    filename = document.original_filename
    headers = {"Content-Disposition": f"attachment; filename={filename}"}
    return Response(content=document_data, headers=headers,
                    media_type=document.document_mimetype)
