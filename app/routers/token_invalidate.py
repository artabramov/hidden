"""FastAPI router for invalidating JWT tokens (logout)."""

from fastapi import APIRouter, Depends, status, Request
from fastapi.responses import JSONResponse
from app.managers.encryption_manager import EncryptionManager
from app.sqlite import get_session
from app.redis import get_cache
from app.models.user import User, UserRole
from app.hook import Hook, HOOK_AFTER_TOKEN_INVALIDATE
from app.auth import auth
from app.repository import Repository
from app.schemas.token_invalidate import TokenInvalidateResponse
from app.helpers.jwt_helper import generate_jti

router = APIRouter()


@router.delete("/auth/token", summary="Invalidate token (logout)",
               response_class=JSONResponse, status_code=status.HTTP_200_OK,
               response_model=TokenInvalidateResponse, tags=["Authentication"])
async def token_invalidate(
    request: Request, session=Depends(get_session), cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.reader))
) -> TokenInvalidateResponse:
    """
    Invalidates the current JWT (logout) by rotating the stored JTI for
    the authenticated user. On success, persists the new JTI, triggers
    the post-invalidate hook, and returns the user ID. The user will
    need to authenticate again to obtain a new valid token.

    **Authentication:**
    - Requires a valid bearer token with `reader` role or higher.

    **Validation schemas:**
    - `TokenInvalidateResponse` — confirms logout by returning the user
    ID.

    **Request body / parameters:**
    - None.

    **Response codes:**
    - `200` — token invalidated; logout successful.
    - `401` — missing, invalid, or expired token.
    - `403` — insufficient role, invalid JTI, user is inactive or
    suspended.
    - `423` — application is temporarily locked.
    - `498` — secret key is missing.
    - `499` — secret key is invalid.

    **Hooks:**
    - `HOOK_AFTER_TOKEN_INVALIDATE`: executes after successful token
    invalidation.
    """
    config = request.app.state.config
    encryption_manager = EncryptionManager(config, request.state.secret_key)

    jti = generate_jti(config.JTI_LENGTH)
    current_user.jti_encrypted = encryption_manager.encrypt_str(jti)
    user_repository = Repository(session, cache, User, config)
    await user_repository.update(current_user)

    hook = Hook(request, session, cache, current_user=current_user)
    await hook.call(HOOK_AFTER_TOKEN_INVALIDATE)

    request.state.log.debug("token invalidated; user_id=%s;", current_user.id)
    return {"user_id": current_user.id}
