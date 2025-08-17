from fastapi import APIRouter, Depends, status, Request
from fastapi.responses import JSONResponse
from app.postgres import get_session
from app.redis import get_cache
from app.models.user_model import User, UserRole
from app.schemas.user_update_schema import (
    UserUpdateRequest, UserUpdateResponse)
from app.error import E, LOC_PATH, ERR_VALUE_ERROR
from app.hook import Hook, HOOK_AFTER_USER_UPDATE
from app.auth import auth
from app.repository import Repository

router = APIRouter()


@router.put("/user/{user_id}", summary="Update a user.",
            response_class=JSONResponse, status_code=status.HTTP_200_OK,
            response_model=UserUpdateResponse, tags=["Users"])
async def user_update(
    user_id: int, schema: UserUpdateRequest, request: Request,
    session=Depends(get_session), cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.reader))
) -> UserUpdateResponse:
    """
    Updates a user. Updates the current user information, such a their
    first name, last name, and user summary.

    **Auth:**
    - The token must be included in the request header and contain auth
    data for an active user with the `reader`, `writer`, `editor`, or
    `admin` role.

    **Returns:**
    - `UserUpdateResponse`: Contains the ID of the updated user.

    **Responses:**
    - `200 OK`: If the user is successfully updated.
    - `401 Unauthorized`: If the token is invalid or lacks permissions.
    - `403 Forbidden`: If the token or secret key is missing.
    - `422 Unprocessable Entity`: If parameters validation fails.
    - `423 Locked`: If the app is locked.

    **Hooks:**
    - `HOOK_AFTER_USER_UPDATE`: Executes after the user is successfully
    updated.
    """
    if user_id != current_user.id:
        raise E([LOC_PATH, "user_id"], user_id,
                ERR_VALUE_ERROR, status.HTTP_422_UNPROCESSABLE_ENTITY)

    current_user.first_name = schema.first_name
    current_user.last_name = schema.last_name
    current_user.user_summary = schema.user_summary

    user_repository = Repository(session, cache, User)
    await user_repository.update(current_user)

    hook = Hook(request.app, session, cache, current_user=current_user)
    await hook.call(HOOK_AFTER_USER_UPDATE, current_user)

    return {"user_id": current_user.id}
