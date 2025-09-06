"""FastAPI router for deleting user accounts."""

from fastapi import APIRouter, Depends, status, Request
from fastapi.responses import JSONResponse
from app.sqlite import get_session
from app.redis import get_cache
from app.models.user import User, UserRole
from app.schemas.user_delete import UserDeleteResponse
from app.repository import Repository
from app.error import E, LOC_PATH, ERR_VALUE_NOT_FOUND, ERR_VALUE_INVALID
from app.hook import Hook, HOOK_AFTER_USER_DELETE
from app.auth import auth

router = APIRouter()


@router.delete("/user/{user_id}", summary="Delete user.",
               response_class=JSONResponse, status_code=status.HTTP_200_OK,
               response_model=UserDeleteResponse, tags=["Users"])
async def user_delete(
    user_id: int, request: Request,
    session=Depends(get_session), cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.admin)),
) -> UserDeleteResponse:
    """
    Deletes a user account by ID. The current user cannot delete their
    own account. The user to delete should not have any relationships
    with other app objects.
    
    **Authentication:**
    - Requires a valid bearer token with the `admin` role.

    **Validation schemas:**
    - `UserDeleteResponse` — confirmation response with the deleted
    user's ID.

    **Path parameters:**
    - `user_id` (integer) — unique identifier of the user to delete.

    **Response codes:**
    - `200` — user successfully deleted.
    - `401` — missing, invalid, or expired token.
    - `403` — insufficient role, invalid JTI, user is inactive or
    suspended.
    - `404` — user not found.
    - `422` — attempted to delete own account or deletion failed.
    - `423` — application is temporarily locked.
    - `498` — secret key is missing.
    - `499` — secret key is invalid.

    **Hooks:**
    - `HOOK_AFTER_USER_DELETE`: executes after successful deletion.
    """
    config = request.app.state.config

    if user_id == current_user.id:
        raise E([LOC_PATH, "user_id"], user_id,
                ERR_VALUE_INVALID, status.HTTP_422_UNPROCESSABLE_ENTITY)

    user_repository = Repository(session, cache, User, config)
    user = await user_repository.select(id=user_id)

    if not user:
        raise E([LOC_PATH, "user_id"], user_id,
                ERR_VALUE_NOT_FOUND, status.HTTP_404_NOT_FOUND)

    try:
        await user_repository.delete(user)
    except Exception:
        raise E([LOC_PATH, "user_id"], user_id,
                ERR_VALUE_INVALID, status.HTTP_422_UNPROCESSABLE_ENTITY)

    hook = Hook(request, session, cache, current_user=current_user)
    await hook.call(HOOK_AFTER_USER_DELETE, user)

    request.state.log.debug("user deleted; user_id=%s;", user.id)
    return {"user_id": user.id}
