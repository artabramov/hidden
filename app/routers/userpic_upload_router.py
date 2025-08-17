import os
import uuid
from fastapi import APIRouter, Depends, status, File, UploadFile, Request
from fastapi.responses import JSONResponse
from app.postgres import get_session
from app.redis import get_cache
from app.models.user_model import User, UserRole
from app.schemas.userpic_upload_schema import UserpicUploadResponse
from app.error import (
    E, LOC_PATH, LOC_BODY, ERR_VALUE_ERROR, ERR_FILE_ERROR)
from app.hook import Hook, HOOK_AFTER_USERPIC_UPLOAD
from app.auth import auth
from app.repository import Repository
from app.managers.file_manager import FileManager
from app.helpers.image_helper import image_resize, IMAGE_MIMETYPES
from app.helpers.encrypt_helper import encrypt_bytes
from app.config import get_config

router = APIRouter()
cfg = get_config()


@router.post("/user/{user_id}/userpic", summary="Upload a userpic.",
             response_class=JSONResponse, status_code=status.HTTP_200_OK,
             response_model=UserpicUploadResponse, tags=["Users"])
async def userpic_upload(
    user_id: int, request: Request, file: UploadFile = File(...),
    session=Depends(get_session), cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.reader))
) -> UserpicUploadResponse:
    """
    Uploads a userpic. Allows the current user to upload a new profile
    picture. If a userpic already exists, it is replaced with the new
    one.

    **Auth:**
    - The token must be included in the request header and contain auth
    data for an active user with the `reader`, `writer`, `editor`, or
    `admin` role.

    **Returns:**
    - `UserpicUploadResponse`: Contains the ID of the user whose profile
    picture was uploaded.

    **Responses:**
    - `200 OK`: If the the profile picture is successfully uploaded.
    - `401 Unauthorized`: If the token is invalid or lacks permissions.
    - `403 Forbidden`: If the token or secret key is missing.
    - `422 Unprocessable Entity`: If parameters validation fails.
    - `423 Locked`: If the app is locked.

    **Hooks:**
    - `HOOK_AFTER_USERPIC_UPLOAD`: Executes after the profile picture is
    successfully created.
    """
    if user_id != current_user.id:
        raise E([LOC_PATH, "user_id"], user_id,
                ERR_VALUE_ERROR, status.HTTP_422_UNPROCESSABLE_ENTITY)

    elif file.content_type not in IMAGE_MIMETYPES:
        raise E([LOC_BODY, "file"], file.filename,
                ERR_FILE_ERROR, status.HTTP_422_UNPROCESSABLE_ENTITY)

    if current_user.has_userpic:
        await FileManager.delete(current_user.userpic_path)

    userpic_filename = str(uuid.uuid4())
    userpic_path = os.path.join(cfg.USERPICS_PATH, userpic_filename)

    await FileManager.upload(file, userpic_path)
    await image_resize(userpic_path, cfg.USERPICS_WIDTH,
                       cfg.USERPICS_HEIGHT, cfg.USERPICS_QUALITY)

    userpic_data = await FileManager.read(userpic_path)
    encrypted_data = encrypt_bytes(userpic_data)
    await FileManager.write(userpic_path, encrypted_data)

    current_user.userpic_filename = userpic_filename

    user_repository = Repository(session, cache, User)
    await user_repository.update(current_user)

    hook = Hook(request.app, session, cache, current_user=current_user)
    await hook.call(HOOK_AFTER_USERPIC_UPLOAD, current_user)

    return {"user_id": current_user.id}
