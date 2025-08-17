from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from app.postgres import get_session
from app.redis import get_cache
from app.models.user_model import User
from app.helpers.jwt_helper import jwt_encode
from app.helpers.encrypt_helper import hash_str
from app.schemas.token_retrieve_schema import (
    TokenRetrieveRequest, TokenRetrieveResponse)
from app.error import (
    E, ERR_VALUE_ERROR, ERR_USER_NOT_LOGGED_IN, LOC_QUERY, ERR_USER_INACTIVE)
from app.hook import Hook, HOOK_AFTER_TOKEN_RETRIEVE
from app.repository import Repository
from app.config import get_config

router = APIRouter()
cfg = get_config()


@router.get("/auth/token", summary="Retrieve a token.",
            response_class=JSONResponse, status_code=status.HTTP_200_OK,
            response_model=TokenRetrieveResponse, tags=["Auth"])
async def token_retrieve(
    schema=Depends(TokenRetrieveRequest),
    session=Depends(get_session), cache=Depends(get_cache)
) -> TokenRetrieveResponse:
    """
    Retrieves a token. Validates the username and the provided
    time-based one-time password (TOTP). If authentication is
    successful, returns a new JWT token.

    **Auth:**
    - No authentication required.

    **Returns:**
    - `TokenRetrieveResponse`: Contains a signed JWT token.

    **Responses:**
    - `200 OK`: Token issued successfully.
    - `403 Forbidden`: If the secret key is missing.
    - `422 Unprocessable Entity`: If parameters validation fails.
    - `423 Locked`: If the app is locked.

    **Hooks:**
    - `HOOK_AFTER_TOKEN_RETRIEVE`: Executes after the token is
    successfully retrieved.
    """
    user_repository = Repository(session, cache, User)

    username_hash = hash_str(schema.username)
    user = await user_repository.select(username_hash__eq=username_hash)

    if not user:
        raise E([LOC_QUERY, "username"], schema.username,
                ERR_VALUE_ERROR, status.HTTP_422_UNPROCESSABLE_ENTITY)

    elif not user.is_active:
        raise E([LOC_QUERY, "username"], schema.username,
                ERR_USER_INACTIVE, status.HTTP_422_UNPROCESSABLE_ENTITY)

    elif not user.password_accepted:
        raise E([LOC_QUERY, "username"], schema.username,
                ERR_USER_NOT_LOGGED_IN,
                status.HTTP_422_UNPROCESSABLE_ENTITY)

    elif schema.user_totp == user.user_totp:
        user.mfa_attempts = 0
        user.password_accepted = False

        await user_repository.update(user)

        hook = Hook(session, cache, current_user=user)
        await hook.call(HOOK_AFTER_TOKEN_RETRIEVE)

        user_token = jwt_encode(user, token_exp=schema.token_exp)
        return {"user_token": user_token}

    else:
        user.mfa_attempts += 1

        if user.mfa_attempts >= cfg.USER_TOTP_ATTEMPTS:
            user.mfa_attempts = 0
            user.password_accepted = False

        await user_repository.update(user)

        raise E([LOC_QUERY, "user_totp"], schema.user_totp,
                ERR_VALUE_ERROR, status.HTTP_422_UNPROCESSABLE_ENTITY)
