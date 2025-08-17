import os
from fastapi import APIRouter, Depends, status, Response
from fastapi.responses import JSONResponse
from app.postgres import get_session
from app.redis import get_cache
from app.models.user_model import User, UserRole
from app.error import E, LOC_PATH, ERR_FILE_NOT_FOUND
from app.helpers.image_helper import IMAGE_MEDIATYPE
from app.managers.file_manager import FileManager
from app.helpers.encrypt_helper import decrypt_bytes
from app.auth import auth
from app.config import get_config
from app.lru import LRU

cfg = get_config()
lru = LRU(cfg.USERPICS_LRU_SIZE)
router = APIRouter()


@router.get("/userpics/{userpic_filename}", summary="Retrieve a userpic.",
            response_class=JSONResponse, status_code=status.HTTP_200_OK,
            tags=["Files"])
async def userpic_retrieve(
    userpic_filename: str,
    session=Depends(get_session), cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.reader))
):
    """
    Retrieves a userpic. If the userpic exists in LRU cache, it will be
    served directly. Otherwise, it will fetch the image from the file
    system.

    **Auth:**
    - The token must be included in the request header and contain auth
    data for an active user with the `reader`, `writer`, `editor`, or
    `admin` role.

    **Returns:**
    - `Response`: Response on success.

    **Responses:**
    - `200 OK`: If the userpic is found and returned successfully.
    - `401 Unauthorized`: If the token is invalid or lacks permissions.
    - `403 Forbidden`: If the token or secret key is missing.
    - `404 Not Found`: If the userpic file does not exist.
    - `423 Locked`: If the app is locked.
    """
    decrypted_data = await lru.load(userpic_filename)
    if not decrypted_data:
        userpic_path = os.path.join(cfg.USERPICS_PATH, userpic_filename)
        encrypted_data = await FileManager.read(userpic_path)
        decrypted_data = decrypt_bytes(encrypted_data)
        await lru.save(userpic_filename, decrypted_data)

    if not decrypted_data:
        raise E([LOC_PATH, "userpic_filename"], userpic_filename,
                ERR_FILE_NOT_FOUND, status.HTTP_404_NOT_FOUND)

    return Response(content=decrypted_data, media_type=IMAGE_MEDIATYPE)
