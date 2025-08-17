from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from app.postgres import get_session
from app.redis import get_cache
from app.models.user_model import User, UserRole
from app.error import E, LOC_PATH, ERR_VALUE_NOT_FOUND
from app.auth import auth
from app.config import get_config
from app.lru import LRU
from app.helpers.encrypt_helper import decrypt_bytes
from app.repository import Repository
from app.models.document_model import Document
from app.models.shard_model import Shard
from app.managers.file_manager import FileManager
from io import BytesIO
from fastapi.responses import StreamingResponse

cfg = get_config()
lru = LRU(cfg.DOCUMENTS_LRU_SIZE)
router = APIRouter()


@router.get("/documents/{document_id}", summary="Download a document.",
            response_class=JSONResponse, status_code=status.HTTP_200_OK,
            tags=["Files"])
async def document_download(
    document_id: int,
    session=Depends(get_session), cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.reader))
) -> StreamingResponse:
    """
    Download a document. Loads the original file by its ID from storage
    (using an LRU cache), and returns the file in the response with
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
    document_repository = Repository(session, cache, Document)
    document = await document_repository.select(id=document_id)

    if not document:
        raise E([LOC_PATH, "document_id"], document_id,
                ERR_VALUE_NOT_FOUND, status.HTTP_404_NOT_FOUND)

    decrypted_data = await lru.load(document_id)
    if not decrypted_data:
        shard_repository = Repository(session, cache, Shard)
        shards = await shard_repository.select_all(
            document_id__eq=document.id, order_by="shard_index", order="asc")
        encrypted_data = await FileManager.merge(
            [shard.shard_path for shard in shards])
        decrypted_data = decrypt_bytes(encrypted_data)
        await lru.save(document_id, decrypted_data)

    filename = document.original_filename
    return StreamingResponse(
        BytesIO(decrypted_data), media_type=document.document_mimetype,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )
