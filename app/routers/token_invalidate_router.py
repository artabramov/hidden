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


@router.delete("/auth/token", summary="Invalidate token",
               response_class=JSONResponse, status_code=status.HTTP_200_OK,
               response_model=TokenDeleteResponse, tags=["Authentication"])
@locked
async def token_invalidate(
    session=Depends(get_session), cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.reader))
) -> TokenDeleteResponse:
    """
    FastAPI router for invalidating the current user's token by updating
    their JTI. Requires the user to have the reader role or higher.
    Returns a 200 response with an empty dictionary upon successful
    invalidation. Returns a 403 error if the user's token is invalid or
    if the user does not have the required role.
    """
    user_repository = Repository(session, cache, User)
    current_user.jti = jti_create()
    await user_repository.update(current_user, commit=False)

    hook = Hook(session, cache, current_user=current_user)
    await hook.do(HOOK_BEFORE_TOKEN_INVALIDATE, current_user)

    await user_repository.commit()
    await hook.do(HOOK_AFTER_TOKEN_INVALIDATE, current_user)

    return {"user_id": current_user.id}
