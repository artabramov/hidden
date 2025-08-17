from fastapi import APIRouter, Depends, status, Request
from app.helpers.lock_helper import lock_enable
from fastapi.responses import JSONResponse
from app.models.user_model import User, UserRole
from app.schemas.lock_create_schema import LockCreateResponse
from app.auth import auth
from app.postgres import get_session
from app.redis import get_cache
from app.hook import Hook, HOOK_AFTER_LOCK_CREATE

router = APIRouter()


@router.post("/lock", summary="Lock the app.",
             response_class=JSONResponse, status_code=status.HTTP_200_OK,
             response_model=LockCreateResponse, tags=["Lock"])
async def lock_create(
    request: Request,
    session=Depends(get_session), cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.admin))
) -> LockCreateResponse:
    """
    Locks the app. Creates a lock that prevents the app from any
    operations. The lock can only be disabled programmatically or
    after app restart.

    **Auth:**
    - The token must be included in the request header and contain auth
    data for an active user with the `admin` role.

    **Returns:**
    - `LockCreateResponse`: Response on success.

    **Responses:**
    - `200 OK`: If the app is successfully locked.
    - `401 Unauthorized`: If the token is invalid or lacks permissions.
    - `403 Forbidden`: If the token or secret key is missing.
    - `423 Locked`: If the app is already locked.

    **Hooks:**
    - `HOOK_AFTER_LOCK_CREATE`: Executes after the lock is successfully
    created.
    """
    await lock_enable()

    hook = Hook(request.app, session, cache, current_user=current_user)
    await hook.call(HOOK_AFTER_LOCK_CREATE)

    return {"lock_exists": True}
