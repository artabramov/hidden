"""FastAPI router for user login (authentication step 1)."""

import time
from fastapi import APIRouter, Depends, status, Request
from fastapi.responses import JSONResponse
from app.sqlite import get_session
from app.redis import get_cache
from app.repository import Repository
from app.managers.encryption_manager import EncryptionManager
from app.schemas.user_login import (
    UserLoginRequest, UserLoginResponse)
from app.models.user import User
from app.constants import CONST_VALUE_OBSCURED
from app.hook import Hook, HOOK_AFTER_USER_LOGIN
from app.error import (
    E, LOC_BODY, ERR_USER_SUSPENDED, ERR_USER_INACTIVE, ERR_VALUE_INVALID)

router = APIRouter()


@router.post("/auth/login", summary="Login (authentication step 1)",
             response_class=JSONResponse, status_code=status.HTTP_200_OK,
             response_model=UserLoginResponse, tags=["Authentication"])
async def user_login(
    request: Request, schema: UserLoginRequest,
    session=Depends(get_session), cache=Depends(get_cache)
) -> UserLoginResponse:
    """
    Authenticates a user. Verifies credentials and denies access for
    suspended or inactive accounts. On success, clears suspension,
    resets the attempt counter, triggers the post-login hook, and
    returns the user ID with a password acceptance flag; on failure,
    increments attempts and may apply a temporary suspension.

    **Authentication:**
    - No prior authentication required.

    **Validation schemas:**
    - `UserLoginRequest` — request body with username and password.
    - `UserLoginResponse` — contains user ID and password acceptance
    flag.

    **Request body**:
    - `username` (string) — login identifier; automatically trimmed
    and lowercased; only Latin letters, digits, and underscore allowed.
    - `password` (string) — login credential.

    **Response codes:**
    - `200` — user successfully authenticated (password accepted).
    - `422` — invalid credentials; user suspended; user inactive.
    - `423` — application is temporarily locked.
    - `498` — gocryptfs key is missing.
    - `499` — gocryptfs key is invalid.

    **Hooks:**
    - `HOOK_AFTER_USER_LOGIN`: executes after successful authentication.
    """
    config = request.app.state.config
    encryption_manager = EncryptionManager(config, request.state.gocryptfs_key)

    password = schema.password.get_secret_value()
    password_hash = encryption_manager.get_hash(password)

    user_repository = Repository(session, cache, User, config)
    user = await user_repository.select(username__eq=schema.username)

    now = int(time.time())

    if not user:
        raise E([LOC_BODY, "username"], schema.username,
                ERR_VALUE_INVALID, status.HTTP_422_UNPROCESSABLE_ENTITY)

    elif user.suspended_until_date > now:
        raise E([LOC_BODY, "username"], schema.username,
                ERR_USER_SUSPENDED, status.HTTP_422_UNPROCESSABLE_ENTITY)

    elif not user.active:
        raise E([LOC_BODY, "username"], schema.username,
                ERR_USER_INACTIVE, status.HTTP_422_UNPROCESSABLE_ENTITY)

    elif user.password_hash == password_hash:
        user.suspended_until_date = 0
        user.password_accepted = True
        user.password_attempts = 0
        await user_repository.update(user)

        hook = Hook(request, session, cache, current_user=user)
        await hook.call(HOOK_AFTER_USER_LOGIN)

        request.state.log.debug("user logged in; user_id=%s;", user.id)
        return {
            "user_id": user.id,
            "password_accepted": True
        }

    else:
        user.password_accepted = False
        user.password_attempts += 1

        if user.password_attempts >= config.AUTH_PASSWORD_ATTEMPTS:
            user.suspended_until_date = now + config.AUTH_SUSPENDED_TIME
            user.password_attempts = 0

        await user_repository.update(user)

        raise E([LOC_BODY, "password"], CONST_VALUE_OBSCURED,
                ERR_VALUE_INVALID, status.HTTP_422_UNPROCESSABLE_ENTITY)
