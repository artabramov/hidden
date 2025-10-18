"""FastAPI router for issuing JWT tokens (authentication step 2)."""

from fastapi import APIRouter, Depends, status, Request
from fastapi.responses import JSONResponse
from app.sqlite import get_session
from app.redis import get_cache
from app.models.user import User
from app.managers.encryption_manager import EncryptionManager
from app.helpers.jwt_helper import create_payload, encode_jwt
from app.helpers.mfa_helper import calculate_totp
from app.schemas.token_retrieve import (
    TokenRetrieveRequest, TokenRetrieveResponse)
from app.error import (
    E, LOC_BODY, ERR_VALUE_INVALID, ERR_USER_NOT_LOGGED_IN, ERR_USER_INACTIVE)
from app.hook import Hook, HOOK_AFTER_TOKEN_RETRIEVE
from app.repository import Repository

router = APIRouter()


@router.post("/auth/token", summary="Issue token (authentication step 2)",
             response_class=JSONResponse, status_code=status.HTTP_200_OK,
             response_model=TokenRetrieveResponse, tags=["Authentication"])
async def token_retrieve(
    request: Request, schema: TokenRetrieveRequest,
    session=Depends(get_session), cache=Depends(get_cache)
) -> TokenRetrieveResponse:
    """
    Completes MFA authentication and issues a JWT access token. Verifies
    the username and the provided time-based one-time password (TOTP).
    On success, resets the attempt counter, clears the password
    acceptance flag, triggers the post-token hook, and returns the user
    ID with a signed JWT. On failure, increments attempts and may force
    the user to restart authentication from the login step.

    **Authentication:**
    - Requires successful password authentication (previous login step).

    **Validation schemas:**
    - `TokenRetrieveRequest` — request body with username, TOTP, and
    optional token expiration.
    - `TokenRetrieveResponse` — contains user ID and JWT token.

    **Request body**:
    - `username` (string) — login identifier; automatically trimmed
    and lowercased; only Latin letters, digits, and underscore allowed.
    - `totp` (string) — one-time password generated from the MFA secret.
    - `exp` (integer) — custom expiration time in seconds for
    the issued JWT.

    **Response codes:**
    - `200` — TOTP validated; token successfully issued.
    - `422` — invalid username, inactive user, user not logged in, or
    invalid TOTP.
    - `423` — application is temporarily locked.
    - `498` — gocryptfs key is missing.
    - `499` — gocryptfs key is invalid.

    **Hooks:**
    - `HOOK_AFTER_TOKEN_RETRIEVE`: executes after successful token
    retrieval.
    """
    config = request.app.state.config
    encryption_manager = EncryptionManager(config, request.state.gocryptfs_key)

    user_repository = Repository(session, cache, User, config)
    user = await user_repository.select(username__eq=schema.username)

    if not user:
        raise E([LOC_BODY, "username"], schema.username,
                ERR_VALUE_INVALID, status.HTTP_422_UNPROCESSABLE_ENTITY)

    elif not user.active:
        raise E([LOC_BODY, "username"], schema.username,
                ERR_USER_INACTIVE, status.HTTP_422_UNPROCESSABLE_ENTITY)

    elif not user.password_accepted:
        raise E([LOC_BODY, "username"], schema.username,
                ERR_USER_NOT_LOGGED_IN, status.HTTP_422_UNPROCESSABLE_ENTITY)

    mfa_secret = encryption_manager.decrypt_str(user.mfa_secret_encrypted)

    if schema.totp == calculate_totp(mfa_secret):
        user.mfa_attempts = 0
        user.password_accepted = False
        await user_repository.update(user)

        jti = encryption_manager.decrypt_str(user.jti_encrypted)
        token_payload = create_payload(user, jti, exp=schema.exp)
        user_token = encode_jwt(
            token_payload, config.JWT_SECRET, config.JWT_ALGORITHMS[0])

        hook = Hook(request, session, cache, current_user=user)
        await hook.call(HOOK_AFTER_TOKEN_RETRIEVE)

        # TODO: Update last login date

        request.state.log.debug("token retrieved; user_id=%s;", user.id)
        return {
            "user_id": user.id,
            "user_token": user_token
        }

    else:
        user.mfa_attempts += 1

        if user.mfa_attempts >= config.AUTH_TOTP_ATTEMPTS:
            user.mfa_attempts = 0
            user.password_accepted = False

        await user_repository.update(user)

        raise E([LOC_BODY, "totp"], schema.totp,
                ERR_VALUE_INVALID, status.HTTP_422_UNPROCESSABLE_ENTITY)
