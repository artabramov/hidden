import uuid
import os
from fastapi import APIRouter, Depends, status, File, UploadFile
from fastapi.responses import JSONResponse
from app.database import get_session
from app.cache import get_cache
from app.decorators.locked_decorator import locked
from app.models.user_model import User, UserRole
from app.schemas.user_schemas import UserpicUploadResponse
from app.errors import E
from app.hooks import Hook
from app.auth import auth
from app.repository import Repository
from app.managers.file_manager import FileManager
from app.helpers.image_helper import image_resize
from app.config import get_config
from app.constants import (
    LOC_PATH, LOC_BODY, ERR_RESOURCE_NOT_FOUND, ERR_RESOURCE_FORBIDDEN,
    ERR_MIMETYPE_UNSUPPORTED, HOOK_BEFORE_USERPIC_UPLOAD,
    HOOK_AFTER_USERPIC_UPLOAD)

router = APIRouter()
cfg = get_config()


@router.post("/user/{user_id}/userpic", summary="Upload userpic",
             response_class=JSONResponse, status_code=status.HTTP_200_OK,
             response_model=UserpicUploadResponse, tags=["Users"])
@locked
async def userpic_upload(
    user_id: int, file: UploadFile = File(...),
    session=Depends(get_session), cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.reader))
) -> UserpicUploadResponse:
    """
    FastAPI router for uploading a userpic. Deletes the existing
    userpic if it exists, uploads and saves a new one, resizes it to
    the specified dimensions, and updates the user's data with the new
    userpic. Allowed for the current user only. Requires the user to
    have a reader role or higher. Returns a 200 response with the
    user ID. Raises a 403 error if the user attempts to upload a
    userpic for a different user, or if the user's token is invalid.
    Raises a 422 error if the file's MIME type is unsupported.
    """
    user_repository = Repository(session, cache, User)
    user = await user_repository.select(id=user_id)

    if not user:
        raise E([LOC_PATH, "user_id"], user_id,
                ERR_RESOURCE_NOT_FOUND, status.HTTP_404_NOT_FOUND)

    elif user_id != current_user.id:
        raise E([LOC_PATH, "user_id"], user_id,
                ERR_RESOURCE_FORBIDDEN, status.HTTP_403_FORBIDDEN)

    elif file.content_type not in cfg.USERPIC_MIMES:
        raise E([LOC_BODY, "file"], user_id,
                ERR_MIMETYPE_UNSUPPORTED, status.HTTP_422_UNPROCESSABLE_ENTITY)

    if current_user.userpic_filename:
        await FileManager.delete(current_user.userpic_path)

    userpic_filename = str(uuid.uuid4()) + cfg.USERPIC_EXTENSION
    userpic_path = os.path.join(cfg.USERPIC_BASE_PATH, userpic_filename)

    hook = Hook(session, cache, current_user=current_user)
    await hook.do(HOOK_BEFORE_USERPIC_UPLOAD, current_user)

    await FileManager.upload(file, userpic_path)
    await image_resize(userpic_path, cfg.USERPIC_WIDTH, cfg.USERPIC_HEIGHT,
                       cfg.USERPIC_QUALITY)

    user_repository = Repository(session, cache, User)
    current_user.userpic_filename = userpic_filename
    await user_repository.update(current_user, commit=False)

    await user_repository.commit()
    await hook.do(HOOK_AFTER_USERPIC_UPLOAD, current_user)

    return {"user_id": current_user.id}
