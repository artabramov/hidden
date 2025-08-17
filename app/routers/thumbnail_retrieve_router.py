import os
from fastapi import APIRouter, Depends, status, Response
from fastapi.responses import JSONResponse
from app.postgres import get_session
from app.redis import get_cache
from app.models.user_model import User, UserRole
from app.error import E, LOC_PATH, ERR_FILE_NOT_FOUND
from app.helpers.image_helper import IMAGE_MEDIATYPE
from app.helpers.encrypt_helper import decrypt_bytes
from app.auth import auth
from app.config import get_config
from app.lru import LRU
from app.managers.file_manager import FileManager

cfg = get_config()
lru = LRU(cfg.THUMBNAILS_LRU_SIZE)
router = APIRouter()


@router.get("/thumbnails/{thumbnail_filename}", summary="Retrieve thumbnail.",
            response_class=JSONResponse, status_code=status.HTTP_200_OK,
            tags=["Files"])
async def thumbnail_retrieve(
    thumbnail_filename: str,
    session=Depends(get_session), cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.reader))
):
    """
    Retrieves a thumbnail. Attempts to load the file by filename from
    the configured thumbnail directory, optionally using an in-memory
    LRU cache for performance.

    **Auth:**
    - The token must be included in the request header and contain auth
    data for an active user with the `reader`, `writer`, `editor`, or
    `admin` role.

    **Returns:**
    - `Response`: The raw thumbnail image content.

    **Responses:**
    - `200 OK`: If the thumbnail is successfully retrieved.
    - `401 Unauthorized`: If the token is invalid or lacks permissions.
    - `403 Forbidden`: If the token or secret key is missing.
    - `404 Not Found`: If the thumbnail is not found.
    - `423 Locked`: If the app is locked.
    """
    decrypted_data = await lru.load(thumbnail_filename)
    if not decrypted_data:
        thumbnail_path = os.path.join(cfg.THUMBNAILS_PATH, thumbnail_filename)
        encrypted_data = await FileManager.read(thumbnail_path)
        decrypted_data = decrypt_bytes(encrypted_data)
        await lru.save(thumbnail_filename, decrypted_data)

    if not decrypted_data:
        raise E([LOC_PATH, "thumbnail_filename"], thumbnail_filename,
                ERR_FILE_NOT_FOUND, status.HTTP_404_NOT_FOUND)

    return Response(content=decrypted_data, media_type=IMAGE_MEDIATYPE)
