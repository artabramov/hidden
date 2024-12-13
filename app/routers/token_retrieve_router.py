import time
from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from app.database import get_session
from app.cache import get_cache
from app.decorators.locked_decorator import locked
from app.models.user_model import User, UserRole
from app.helpers.jwt_helper import jwt_encode
from app.schemas.user_schemas import (
    TokenRetrieveRequest, TokenRetrieveResponse)
from app.errors import E
from app.hooks import Hook
from app.repository import Repository
from app.config import get_config
from app.constants import (
    LOC_QUERY, ERR_USER_INACTIVE, ERR_VALUE_INVALID,
    ERR_USER_PASSWORD_NOT_ACCEPTED, HOOK_BEFORE_TOKEN_RETRIEVE,
    HOOK_AFTER_TOKEN_RETRIEVE)

router = APIRouter()
cfg = get_config()


@router.get("/auth/token", summary="Retrieve a token.",
            response_class=JSONResponse, status_code=status.HTTP_200_OK,
            response_model=TokenRetrieveResponse, tags=["Authentication"])
@locked
async def token_retrieve(
    schema=Depends(TokenRetrieveRequest),
    session=Depends(get_session), cache=Depends(get_cache)
) -> TokenRetrieveResponse:
    """
    Retrieve a token. This router retrieves a JWT token for the user
    after validating the one-time password (TOTP). The user must be
    active and have accepted the password in the previous step. Returns
    a 200 response with the token on success, a 403 error if the user
    is inactive, a 422 error if the TOTP is incorrect, and a 423 error
    if the application is locked.

    **Returns:**
    - `TokenRetrieveResponse`: A response schema containing the
    JWT token upon success.

    **Raises:**
    - `403 Forbidden`: Raised if the user is inactive.
    - `422 Unprocessable Entity`: Raised if the TOTP is incorrect or
    invalid.
    - `423 Locked`: Raised if the application is locked.

    **Hooks:**
    - `HOOK_BEFORE_TOKEN_RETRIEVE`: Executes before retrieving the token.
    - `HOOK_AFTER_TOKEN_RETRIEVE`: Executes after the token is retrieved.

    **Auth:**
    - The user must provide a valid `JWT token` in the request header.
    - The `reader`, `writer`, `editor` or `admin` role is required to
    access this router.
    """
    user_repository = Repository(session, cache, User)
    user = await user_repository.select(user_login__eq=schema.user_login)

    if not user:
        raise E([LOC_QUERY, "user_login"], schema.user_login,
                ERR_VALUE_INVALID, status.HTTP_422_UNPROCESSABLE_ENTITY)

    admin_exists = await user_repository.exists(
        user_role__eq=UserRole.admin, is_active__eq=True)

    if not user.is_active and admin_exists:
        raise E([LOC_QUERY, "user_login"], schema.user_login,
                ERR_USER_INACTIVE, status.HTTP_403_FORBIDDEN)

    elif not user.password_accepted:
        raise E([LOC_QUERY, "user_totp"], schema.user_totp,
                ERR_USER_PASSWORD_NOT_ACCEPTED,
                status.HTTP_422_UNPROCESSABLE_ENTITY)

    totp_accepted = schema.user_totp == user.user_totp

    if totp_accepted:
        user.last_login_date = time.time()
        user.mfa_attempts = 0
        user.password_accepted = False

        if not admin_exists:
            user.is_active = True
            user.user_role = UserRole.admin

    else:
        user.mfa_attempts += 1

        if user.mfa_attempts >= cfg.USER_MFA_ATTEMPTS:
            user.mfa_attempts = 0
            user.password_accepted = False

    await user_repository.update(user, commit=False)
    user_token = jwt_encode(user, token_exp=schema.token_exp)

    hook = Hook(session, cache)
    await hook.do(HOOK_BEFORE_TOKEN_RETRIEVE, user)

    await user_repository.commit()
    await hook.do(HOOK_AFTER_TOKEN_RETRIEVE, user)

    if totp_accepted:
        return {"user_token": user_token}

    else:
        raise E([LOC_QUERY, "user_totp"], schema.user_totp,
                ERR_VALUE_INVALID, status.HTTP_422_UNPROCESSABLE_ENTITY)
