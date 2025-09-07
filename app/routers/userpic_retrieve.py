"""FastAPI router for retrieving user image."""

import os
from fastapi import APIRouter, Depends, status, Response, Request
from app.sqlite import get_session
from app.redis import get_cache
from app.models.user import User, UserRole
from app.error import E, LOC_PATH, ERR_VALUE_NOT_FOUND,ERR_FILE_NOT_FOUND
from app.helpers.image_helper import IMAGE_MEDIATYPE
from app.hook import Hook, HOOK_AFTER_USERPIC_RETRIEVE
from app.auth import auth
from app.repository import Repository

router = APIRouter()


@router.get("/user/{user_id}/userpic", summary="Retrieve userpic",
            response_class=Response, status_code=status.HTTP_200_OK,
            tags=["Users"])
async def userpic_retrieve(
    user_id: int, request: Request,
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
    lru = request.app.state.lru
    file_manager = request.app.state.file_manager

    user_repository = Repository(session, cache, User, config)
    user = await user_repository.select(id=user_id)

    if not user:
        raise E([LOC_PATH, "user_id"], user_id,
                ERR_VALUE_NOT_FOUND, status.HTTP_404_NOT_FOUND)

    elif not user.has_thumbnail:
        raise E([LOC_PATH, "user_id"], user_id,
                ERR_FILE_NOT_FOUND, status.HTTP_404_NOT_FOUND)

    userpic_path = os.path.join(
        config.THUMBNAILS_DIR, user.user_thumbnail.filename)
    userpic_data = lru.load(userpic_path)

    if userpic_data is None:
        userpic_data = await file_manager.read(userpic_path)

    if userpic_data is None:
        raise E([LOC_PATH, "user_id"], user_id,
                ERR_FILE_NOT_FOUND, status.HTTP_404_NOT_FOUND)

    lru.save(userpic_path, userpic_data)

    hook = Hook(request, session, cache, current_user=current_user)
    await hook.call(HOOK_AFTER_USERPIC_RETRIEVE, user)

    request.state.log.debug("userpic retrieved; user_id=%s;", user.id)
    return Response(content=userpic_data, media_type=IMAGE_MEDIATYPE)
