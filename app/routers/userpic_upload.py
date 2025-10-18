"""FastAPI router for uploading userpics."""

import uuid
from fastapi import (
    APIRouter, Depends, status, UploadFile, Request, Path,
    File as Data
)
from fastapi.responses import JSONResponse
from app.sqlite import get_session
from app.redis import get_cache
from app.models.user import User, UserRole
from app.models.user_thumbnail import UserThumbnail
from app.schemas.userpic_upload import UserpicUploadResponse
from app.error import (
    E, LOC_PATH, LOC_BODY, ERR_VALUE_INVALID, ERR_FILE_MIMETYPE_INVALID)
from app.hook import Hook, HOOK_AFTER_USERPIC_UPLOAD
from app.auth import auth
from app.repository import Repository
from app.helpers.image_helper import image_resize, IMAGE_MIMETYPES

router = APIRouter()


@router.post(
    "/user/{user_id}/userpic",
    status_code=status.HTTP_200_OK,
    response_class=JSONResponse,
    response_model=UserpicUploadResponse,
    summary="Upload userpic",
    tags=["Users"]
)
async def userpic_upload(
    request: Request,
    data: UploadFile = Data(...),
    user_id: int = Path(..., ge=1),
    session=Depends(get_session),
    cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.reader))
) -> UserpicUploadResponse:
    """
    Uploads a userpic for the authenticated user. The path user ID must
    match the current user. The file must be a standard raster image
    (JPEG, PNG, GIF, BMP, TIFF, ICO, PBM/PGM/PPM) and will be resized
    and re-encoded to JPEG; on success, any previous thumbnail is
    deleted and the new image is saved at the configured dimensions
    and quality.

    **Authentication:**
    - Requires a valid bearer token with `reader` role or higher.

    **Validation schemas:**
    - `UserpicUploadResponse` — confirmation with the user ID.

    **Path parameters:**
    - `user_id` (integer) — identifier of the user uploading the image.

    **Request body:**
    - `file` (multipart/form-data) — image to upload; content type must
    be in the configured image MIME allowlist.

    **Response codes:**
    - `200` — userpic successfully uploaded and stored.
    - `401` — missing, invalid, or expired token.
    - `403` — insufficient role, invalid JTI, user is inactive or
    suspended.
    - `422` — path user ID does not match current user or file mimetype
    is invalid.
    - `423` — application is temporarily locked.
    - `498` — gocryptfs key is missing.
    - `499` — gocryptfs key is invalid.

    **Hooks:**
    - `HOOK_AFTER_USERPIC_UPLOAD`: executes after the image is processed
    and saved.
    """
    config = request.app.state.config
    file_manager = request.app.state.file_manager
    user_repository = Repository(session, cache, User, config)

    if user_id != current_user.id:
        raise E([LOC_PATH, "user_id"], user_id,
                ERR_VALUE_INVALID, status.HTTP_422_UNPROCESSABLE_ENTITY)

    elif data.content_type not in IMAGE_MIMETYPES:
        raise E([LOC_BODY, "file"], data.filename,
                ERR_FILE_MIMETYPE_INVALID,
                status.HTTP_422_UNPROCESSABLE_ENTITY)

    if current_user.has_thumbnail:
        userpic_path = current_user.user_thumbnail.path(config)
        await file_manager.delete(userpic_path)

        current_user.user_thumbnail = None
        await user_repository.update(current_user)

    userpic_uuid = str(uuid.uuid4())
    userpic_path = UserThumbnail.path_for_uuid(config, userpic_uuid)

    await file_manager.upload(data, userpic_path)
    await image_resize(
        userpic_path, config.THUMBNAILS_WIDTH,
        config.THUMBNAILS_HEIGHT, config.THUMBNAILS_QUALITY)

    userpic_filesize = await file_manager.filesize(userpic_path)
    userpic_checksum = await file_manager.checksum(userpic_path)

    user_thumbnail = UserThumbnail(
        current_user.id, userpic_uuid,
        userpic_filesize, userpic_checksum)

    current_user.user_thumbnail = user_thumbnail
    await user_repository.update(current_user)

    hook = Hook(request, session, cache, current_user=current_user)
    await hook.call(HOOK_AFTER_USERPIC_UPLOAD)

    return {"user_id": current_user.id}
