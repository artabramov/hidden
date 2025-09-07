"""FastAPI router for deleting user image."""

import os
from fastapi import APIRouter, Depends, status, Request
from fastapi.responses import JSONResponse
from app.sqlite import get_session
from app.redis import get_cache
from app.models.user import User, UserRole
from app.schemas.userpic_delete import UserpicDeleteResponse
from app.error import E, LOC_PATH, ERR_VALUE_INVALID, ERR_VALUE_NOT_FOUND
from app.hook import Hook, HOOK_AFTER_USERPIC_DELETE
from app.auth import auth
from app.repository import Repository

router = APIRouter()


@router.delete("/user/{user_id}/userpic", summary="Delete userpic",
               response_class=JSONResponse, status_code=status.HTTP_200_OK,
               response_model=UserpicDeleteResponse, tags=["Users"])
async def userpic_delete(
    user_id: int, request: Request,
    session=Depends(get_session), cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.reader))
) -> UserpicDeleteResponse:
    """
    Delete the current user's userpic and return the user ID. Only the
    owner can delete their own userpic.

    **Authentication:**
    - Requires a valid bearer token with `reader` role or higher.

    **Validation schemas:**
    - `UserpicDeleteResponse` — contains the user ID.

    **Path parameters:**
    - `user_id` (integer): target user ID; must equal the authenticated
    user's ID.

    **Response codes:**
    - `200` — userpic successfully deleted.
    - `401` — missing, invalid, or expired token.
    - `403` — insufficient role, invalid JTI, user is inactive or
    suspended.
    - `404` — userpic not found for the user.
    - `422` — user ID does not match the authenticated user.
    - `423` — application is temporarily locked.
    - `498` — secret key is missing.
    - `499` — secret key is invalid.

    **Side effects:**
    - Evicts the thumbnail from the in-memory LRU cache.
    - Deletes the file at `thumbnails/<filename>`.

    **Hooks:**
    - `HOOK_AFTER_USERPIC_DELETE`: executed after successful userpic
    deletion.
    """
    config = request.app.state.config
    lru = request.app.state.lru
    file_manager = request.app.state.file_manager

    if user_id != current_user.id:
        raise E([LOC_PATH, "user_id"], user_id,
                ERR_VALUE_INVALID, status.HTTP_422_UNPROCESSABLE_ENTITY)

    elif not current_user.has_thumbnail:
        raise E([LOC_PATH, "user_id"], user_id,
                ERR_VALUE_NOT_FOUND, status.HTTP_404_NOT_FOUND)

    userpic_path = os.path.join(
        config.THUMBNAILS_DIR, current_user.user_thumbnail.filename)

    lru.delete(userpic_path)
    await file_manager.delete(userpic_path)

    current_user.user_thumbnail = None
    user_repository = Repository(session, cache, User, config)
    await user_repository.update(current_user)

    hook = Hook(request, session, cache, current_user=current_user)
    await hook.call(HOOK_AFTER_USERPIC_DELETE)

    request.state.log.debug("userpic deleted; user_id=%s;", current_user.id)
    return {"user_id": current_user.id}
