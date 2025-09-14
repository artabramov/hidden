"""FastAPI router for retrieving user image."""

import os
from fastapi import APIRouter, Depends, status, Response, Request, Path
from app.sqlite import get_session
from app.redis import get_cache
from app.models.user import User, UserRole
from app.error import (
    E, LOC_PATH, ERR_VALUE_NOT_FOUND, ERR_FILE_NOT_FOUND,
    ERR_FILE_HASH_MISMATCH)
from app.helpers.image_helper import IMAGE_MEDIATYPE
from app.hook import Hook, HOOK_AFTER_USERPIC_RETRIEVE
from app.auth import auth
from app.repository import Repository

router = APIRouter()


@router.get("/user/{user_id}/userpic", summary="Retrieve userpic",
            response_class=Response, status_code=status.HTTP_200_OK,
            tags=["Users"])
async def userpic_retrieve(
    request: Request, user_id: int = Path(..., ge=1),
    session=Depends(get_session), cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.reader))
):
    """
    Retrieve a user's current userpic and return raw image bytes. The
    image bytes are fetched from the LRU cache first, and if absent,
    read from the filesystem and cached.

    **Authentication:**
    - Requires a valid bearer token with `reader` role or higher.

    **Path parameters:**
    - `user_id` (integer): target user identifier.

    **Response:**
    - Raw binary image.

    **Response codes:**
    - `200` — userpic returned.
    - `401` — missing, invalid, or expired token.
    - `403` — insufficient role, invalid JTI, user is inactive or
    suspended.
    - `404` — user not found, no userpic set, or file not found.
    - `423` — application is temporarily locked.
    - `498` — secret key is missing.
    - `499` — secret key is invalid.

    **Side effects:**
    - Reads the image from the LRU cache or filesystem and saves it
    into the LRU cache on hit/miss.

    **Hooks:**
    - `HOOK_AFTER_USERPIC_RETRIEVE`: executed after successful userpic
    retrieval.
    """

    config = request.app.state.config
    file_manager = request.app.state.file_manager
    lru = request.app.state.lru

    user_repository = Repository(session, cache, User, config)
    user = await user_repository.select(id=user_id)

    if not user:
        raise E([LOC_PATH, "user_id"], user_id,
                ERR_VALUE_NOT_FOUND, status.HTTP_404_NOT_FOUND)

    elif not user.has_thumbnail:
        raise E([LOC_PATH, "user_id"], user_id,
                ERR_FILE_NOT_FOUND, status.HTTP_404_NOT_FOUND)

    file_path = os.path.join(config.THUMBNAILS_DIR, user.user_thumbnail.uuid)
    file_data = lru.load(file_path)

    if file_data is None:
        file_exists = await file_manager.isfile(file_path)
        if not file_exists:
            raise E([LOC_PATH, "user_id"], user_id,
                    ERR_FILE_NOT_FOUND, status.HTTP_404_NOT_FOUND)

        file_checksum = await file_manager.checksum(file_path)
        if user.user_thumbnail.checksum != file_checksum:
            raise E([LOC_PATH, "user_id"], user_id,
                    ERR_FILE_HASH_MISMATCH, status.HTTP_404_NOT_FOUND)

        file_data = await file_manager.read(file_path)

    lru.save(file_path, file_data)

    headers = {
        "ETag": f'"{user.user_thumbnail.checksum}"',
        "Content-Disposition": "inline",
        "Content-Length": str(user.user_thumbnail.filesize),
    }

    hook = Hook(request, session, cache, current_user=current_user)
    await hook.call(HOOK_AFTER_USERPIC_RETRIEVE, user)

    request.state.log.debug("userpic retrieved; user_id=%s;", user.id)
    return Response(
        content=file_data, media_type=IMAGE_MEDIATYPE, headers=headers)
