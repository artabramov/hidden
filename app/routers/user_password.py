"""FastAPI router for changing user password."""

from fastapi import APIRouter, Depends, status, Request, Path
from fastapi.responses import JSONResponse
from app.sqlite import get_session
from app.redis import get_cache
from app.models.user import User, UserRole
from app.schemas.user_password import (
    UserPasswordRequest, UserPasswordResponse)
from app.error import E, LOC_PATH, LOC_BODY, ERR_VALUE_INVALID
from app.hook import Hook, HOOK_AFTER_USER_PASSWORD
from app.constants import CONST_VALUE_OBSCURED
from app.auth import auth
from app.repository import Repository
from app.managers.encryption_manager import EncryptionManager

router = APIRouter()


@router.put("/user/{user_id}/password", summary="Change user's password",
            response_class=JSONResponse, status_code=status.HTTP_200_OK,
            response_model=UserPasswordResponse, tags=["Users"])
async def user_password(
    request: Request, schema: UserPasswordRequest,
    user_id: int = Path(..., ge=1),
    session=Depends(get_session), cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.reader))
) -> UserPasswordResponse:
    """
    Changes the password for the authenticated user. The path user ID
    must match the current user, and the new password must differ from
    the current password.

    **Authentication:**
    - Requires a valid bearer token with `reader` role or higher.

    **Validation schemas:**
    - `UserPasswordRequest` — current and new passwords (new password
    must satisfy complexity rules).
    - `UserPasswordResponse` — confirmation with user ID.

    **Path parameters:**
    - `user_id` (integer) — ID of the user whose password is updated
    (must equal the authenticated user's ID).

    **Response codes:**
    - `200` — password successfully changed.
    - `401` — missing, invalid, or expired token.
    - `403` — insufficient role, invalid JTI, user is inactive or
    suspended.
    - `422` — path user ID mismatch, current password invalid, or new
      password equals the current one.
    - `423` — application is temporarily locked.
    - `498` — gocryptfs key is missing.
    - `499` — gocryptfs key is invalid.

    **Hooks:**
    - `HOOK_AFTER_USER_PASSWORD`: executes after password change.
    """
    config = request.app.state.config

    if user_id != current_user.id:
        raise E([LOC_PATH, "user_id"], user_id,
                ERR_VALUE_INVALID, status.HTTP_422_UNPROCESSABLE_ENTITY)

    encryption_manager = EncryptionManager(config, request.state.gocryptfs_key)
    password_hash = encryption_manager.get_hash(schema.current_password)

    if current_user.password_hash != password_hash:
        raise E([LOC_BODY, "current_password"], CONST_VALUE_OBSCURED,
                ERR_VALUE_INVALID, status.HTTP_422_UNPROCESSABLE_ENTITY)

    elif schema.current_password == schema.updated_password:
        raise E([LOC_BODY, "updated_password"], CONST_VALUE_OBSCURED,
                ERR_VALUE_INVALID, status.HTTP_422_UNPROCESSABLE_ENTITY)

    current_user.password_hash = encryption_manager.get_hash(
        schema.updated_password)

    user_repository = Repository(session, cache, User, config)
    await user_repository.update(current_user)

    hook = Hook(request, session, cache, current_user=current_user)
    await hook.call(HOOK_AFTER_USER_PASSWORD)

    request.state.log.debug("password changed; user_id=%s;", current_user.id)
    return {"user_id": current_user.id}
