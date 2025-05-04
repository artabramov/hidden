from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from app.postgres import get_session
from app.redis import get_cache
from app.models.user_model import User, UserRole
from app.hook import Hook, HOOK_AFTER_TOKEN_INVALIDATE
from app.auth import auth
from app.repository import Repository
from app.schemas.token_invalidate_schema import TokenInvalidateResponse
from app.helpers.jwt_helper import generate_jti

router = APIRouter()


@router.delete("/auth/token", summary="Invalidate a token.",
               response_class=JSONResponse, status_code=status.HTTP_200_OK,
               response_model=TokenInvalidateResponse, tags=["Auth"])
async def token_invalidate(
    session=Depends(get_session), cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.reader))
) -> TokenInvalidateResponse:
    """
    Invalidates a token. It generates a new token identifier for the
    current user. The user will need to authenticate again to obtain
    a new valid token.

    **Auth:**
    - The token must be included in the request header and contain auth
    data for an active user with the `reader`, `writer`, `editor`, or
    `admin` role.

    **Returns:**
    - `TokenInvalidateResponse`: Contains the ID of the user whose
    token was invalidated.

    **Responses:**
    - `200 OK`: If the token is successfully invalidated.
    - `401 Unauthorized`: If the token is invalid or lacks permissions.
    - `403 Forbidden`: If the token or secret key is missing.
    - `423 Locked`: If the app is locked.

    **Hooks:**
    - `HOOK_AFTER_USER_ROLE`: Executes after the token is successfully
    invalidated.
    """
    current_user.jti = generate_jti()
    user_repository = Repository(session, cache, User)
    await user_repository.update(current_user)

    hook = Hook(session, cache, current_user=current_user)
    await hook.call(HOOK_AFTER_TOKEN_INVALIDATE)

    return {"user_id": current_user.id}
