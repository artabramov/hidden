import time
from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from app.postgres import get_session
from app.redis import get_cache
from app.models.user_model import User
from app.helpers.encrypt_helper import hash_str
from app.schemas.user_login_schema import UserLoginRequest, UserLoginResponse
from app.error import (
    E, LOC_BODY, ERR_VALUE_ERROR, ERR_USER_SUSPENDED, ERR_USER_INACTIVE)
from app.hook import Hook, HOOK_AFTER_USER_LOGIN
from app.repository import Repository
from app.context import get_context
from app.config import get_config

cfg = get_config()
ctx = get_context()
router = APIRouter()


@router.post("/auth/login", summary="Login a user.",
             response_class=JSONResponse, status_code=status.HTTP_200_OK,
             response_model=UserLoginResponse, tags=["Auth"])
async def user_login(
    schema: UserLoginRequest,
    session=Depends(get_session), cache=Depends(get_cache)
) -> UserLoginResponse:
    """
    Logs in a user. Authenticates the user by username and password.
    If successful, it grants access to the second step of authentication
    and returns an indication of successful login. In case of incorrect
    login attempts, it handles password attempts and can temporarily
    suspend the user if they reached the maximum number of allowed
    failed attempts.

    **Auth:**
    - No authentication required.

    **Returns:**
    - `UserLoginResponse`: Contains the login status on success.

    **Responses:**
    - `200 OK`: If the login is successful, indicating the user's
    credentials are correct.
    - `403 Forbidden`: If the secret key is missing.
    - `422 Unprocessable Entity`: If parameters validation fails.
    - `423 Locked`: If the app is locked.

    **Hooks:**
    - `HOOK_AFTER_USER_LOGIN`: Executes after the user is successfully
    logged in.
    """
    user_repository = Repository(session, cache, User)

    username_hash = hash_str(schema.username)
    user = await user_repository.select(username_hash__eq=username_hash)

    if not user:
        raise E([LOC_BODY, "username"], schema.username,
                ERR_VALUE_ERROR, status.HTTP_422_UNPROCESSABLE_ENTITY)

    elif user.suspended_date + cfg.USER_SUSPENDED_TIME > int(time.time()):
        raise E([LOC_BODY, "username"], schema.username,
                ERR_USER_SUSPENDED, status.HTTP_422_UNPROCESSABLE_ENTITY)

    elif not user.is_active:
        raise E([LOC_BODY, "username"], schema.username,
                ERR_USER_INACTIVE, status.HTTP_422_UNPROCESSABLE_ENTITY)

    elif user.password_hash == hash_str(schema.password):
        user.password_accepted = True
        user.password_attempts = 0
        await user_repository.update(user, commit=False)

        hook = Hook(session, cache, current_user=user)
        await hook.call(HOOK_AFTER_USER_LOGIN)

        return {"password_accepted": True}

    else:
        user.password_accepted = False
        if user.password_attempts >= cfg.USER_PASSWORD_ATTEMPTS - 1:
            user.suspended_date = int(time.time())
            user.password_attempts = 0

        else:
            user.suspended_date = 0
            user.password_attempts += 1

        await user_repository.update(user)

        raise E([LOC_BODY, "password"], schema.password,
                ERR_VALUE_ERROR, status.HTTP_422_UNPROCESSABLE_ENTITY)
