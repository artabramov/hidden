from fastapi import APIRouter, Depends, status, Request
from fastapi.responses import JSONResponse
from app.postgres import get_session
from app.redis import get_cache
from app.models.user_model import User, UserRole
from app.helpers.encrypt_helper import hash_str
from app.schemas.user_password_schema import (
    UserPasswordRequest, UserPasswordResponse)
from app.error import E, LOC_PATH, LOC_BODY, ERR_VALUE_ERROR
from app.hook import Hook, HOOK_AFTER_USER_PASSWORD
from app.auth import auth
from app.repository import Repository

router = APIRouter()


@router.put("/user/{user_id}/password", summary="Change a password.",
            response_class=JSONResponse, status_code=status.HTTP_200_OK,
            response_model=UserPasswordResponse, tags=["Users"])
async def user_password(
    user_id: int, schema: UserPasswordRequest, request: Request,
    session=Depends(get_session), cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.reader))
) -> UserPasswordResponse:
    """
    Changes a password. Fetches the user from the authentication,
    validates the current and new passwords, and updates the password.
    The current user can only change their own password.

    **Auth:**
    - The token must be included in the request header and contain auth
    data for an active user with the `reader`, `writer`, `editor`, or
    `admin` role.

    **Returns:**
    - `UserPasswordResponse`: Containing the ID of the user whose
    password is updated.

    **Responses:**
    - `200 OK`: If the password change is successful.
    - `401 Unauthorized`: If the token is invalid or lacks permissions.
    - `403 Forbidden`: If the token or secret key is missing.
    - `422 Unprocessable Entity`: If parameters validation fails.
    - `423 Locked`: If the app is locked.

    **Hooks:**
    - `HOOK_AFTER_USER_PASSWORD`: Executes after the password is
    successfully changed.
    """
    if user_id != current_user.id:
        raise E([LOC_PATH, "user_id"], user_id,
                ERR_VALUE_ERROR, status.HTTP_422_UNPROCESSABLE_ENTITY)

    elif hash_str(schema.current_password) != current_user.password_hash:
        raise E([LOC_BODY, "current_password"], schema.current_password,
                ERR_VALUE_ERROR, status.HTTP_422_UNPROCESSABLE_ENTITY)

    elif schema.current_password == schema.updated_password:
        raise E([LOC_BODY, "updated_password"], user_id,
                ERR_VALUE_ERROR, status.HTTP_422_UNPROCESSABLE_ENTITY)

    current_user.password_hash = hash_str(schema.updated_password)

    user_repository = Repository(session, cache, User)
    await user_repository.update(current_user)

    hook = Hook(request.app, session, cache, current_user=current_user)
    await hook.call(HOOK_AFTER_USER_PASSWORD, current_user)

    return {"user_id": current_user.id}
