"""FastAPI router for updating user profile."""

from fastapi import APIRouter, Depends, status, Request, Path
from fastapi.responses import JSONResponse
from app.sqlite import get_session
from app.redis import get_cache
from app.models.user import User, UserRole
from app.schemas.user_update import (
    UserUpdateRequest, UserUpdateResponse)
from app.error import E, LOC_PATH, ERR_VALUE_INVALID
from app.hook import Hook, HOOK_AFTER_USER_UPDATE
from app.auth import auth
from app.repository import Repository

router = APIRouter()


@router.put("/user/{user_id}", summary="Update user.",
            response_class=JSONResponse, status_code=status.HTTP_200_OK,
            response_model=UserUpdateResponse, tags=["Users"])
async def user_update(
    request: Request, schema: UserUpdateRequest,
    user_id: int = Path(..., ge=1),
    session=Depends(get_session), cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.reader))
) -> UserUpdateResponse:
    """
    Updates the authenticated user's profile details (first and last
    names and optional summary). The path user ID must match the current
    user.

    **Authentication:**
    - Requires a valid bearer token with `reader` role or higher.

    **Validation schemas:**
    - `UserUpdateRequest` — first name, last name, optional summary.
    - `UserUpdateResponse` — confirmation with user ID.

    **Path parameters:**
    - `user_id` (integer) — ID of the user whose profile is updated
    (must equal the authenticated user's ID).

    **Response codes:**
    - `200` — profile successfully updated.
    - `401` — missing, invalid, or expired token.
    - `403` — insufficient role, invalid JTI, user is inactive or
    suspended.
    - `422` — path user ID mismatch.
    - `423` — application is temporarily locked.
    - `498` — secret key is missing.
    - `499` — secret key is invalid.

    **Hooks:**
    - `HOOK_AFTER_USER_UPDATE`: executes after profile update.
    """
    config = request.app.state.config

    if user_id != current_user.id:
        raise E([LOC_PATH, "user_id"], user_id,
                ERR_VALUE_INVALID, status.HTTP_422_UNPROCESSABLE_ENTITY)

    current_user.first_name = schema.first_name
    current_user.last_name = schema.last_name
    current_user.summary = schema.summary

    user_repository = Repository(session, cache, User, config)
    await user_repository.update(current_user)

    hook = Hook(request, session, cache, current_user=current_user)
    await hook.call(HOOK_AFTER_USER_UPDATE)

    request.state.log.debug("user updated; user_id=%s;", current_user.id)
    return {"user_id": current_user.id}
