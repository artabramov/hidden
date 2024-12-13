from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from app.database import get_session
from app.cache import get_cache
from app.decorators.locked_decorator import locked
from app.models.user_model import User, UserRole
from app.helpers.jwt_helper import jti_create
from app.hooks import Hook
from app.auth import auth
from app.repository import Repository
from app.schemas.user_schemas import TokenDeleteResponse
from app.constants import (
    HOOK_BEFORE_TOKEN_INVALIDATE, HOOK_AFTER_TOKEN_INVALIDATE)

router = APIRouter()


@router.delete("/auth/token", summary="Invalidate a token.",
               response_class=JSONResponse, status_code=status.HTTP_200_OK,
               response_model=TokenDeleteResponse, tags=["Authentication"])
@locked
async def token_invalidate(
    session=Depends(get_session), cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.reader))
) -> TokenDeleteResponse:
    """
    Invalidate a token. This router updates the JTI of the current user
    to invalidate their token. It requires the user to have any role.
    The corresponding hooks are executed, and an empty JSON response is
    returned. Returns a 200 status code on success, a 403 status code
    if authentication fails or the user does not have the required
    permissions, and a 423 status code if the application is locked.

    **Returns:**
    - `TokenDeleteResponse`: A response schema indicating the user ID
      for which the token was invalidated.

    **Raises:**
    - `403 Forbidden`: Raised if the user is not authenticated or does
      not have the required permissions.
    - `423 Locked`: Raised if the application is locked.

    **Hooks:**
    - `HOOK_BEFORE_TOKEN_INVALIDATE`: Executes before invalidating the
      token.
    - `HOOK_AFTER_TOKEN_INVALIDATE`: Executes after the token has been
      invalidated.

    **Auth:**
    - The user must provide a valid `JWT token` in the request header.
    - The `reader`, `writer`, `editor` or `admin` role is required to
      access this router.
    """
    user_repository = Repository(session, cache, User)
    current_user.jti = jti_create()
    await user_repository.update(current_user, commit=False)

    hook = Hook(session, cache, current_user=current_user)
    await hook.do(HOOK_BEFORE_TOKEN_INVALIDATE, current_user)

    await user_repository.commit()
    await hook.do(HOOK_AFTER_TOKEN_INVALIDATE, current_user)

    return {"user_id": current_user.id}
