"""FastAPI router for managing user roles and active status."""

from fastapi import APIRouter, Depends, status, Request, Path
from fastapi.responses import JSONResponse
from app.sqlite import get_session
from app.redis import get_cache
from app.models.user import User, UserRole
from app.schemas.user_role import UserRoleRequest, UserRoleResponse
from app.error import E, LOC_PATH, ERR_VALUE_NOT_FOUND, ERR_VALUE_INVALID
from app.hook import Hook, HOOK_AFTER_USER_ROLE
from app.auth import auth
from app.repository import Repository

router = APIRouter()


@router.put("/user/{user_id}/role",
            summary="Change user's role or active status",
            response_class=JSONResponse, status_code=status.HTTP_200_OK,
            response_model=UserRoleResponse, tags=["Users"])
async def user_role(
    request: Request, schema: UserRoleRequest,
    user_id: int = Path(..., ge=1),
    session=Depends(get_session), cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.admin))
) -> UserRoleResponse:
    """
    Changes the role and active status of a specific user account.
    The current user cannot update their own role or activity status.

    **Authentication:**
    - Requires a valid bearer token with the `admin` role.

    **Validation schemas:**
    - `UserRoleRequest` — request body containing the new role and
    active status values.
    - `UserRoleResponse` — confirmation response with the affected
    user's ID.

    **Path parameters:**
    - `user_id` (integer) — unique identifier of the user whose role or
    status should be updated.

    **Response codes:**
    - `200` — user role or active status successfully updated.
    - `401` — missing, invalid, or expired token.
    - `403` — insufficient role, invalid JTI, user is inactive or
    suspended.
    - `404` — user not found.
    - `422` — attempted to change own role or active status.
    - `423` — application is temporarily locked.
    - `498` — secret key is missing.
    - `499` — secret key is invalid.

    **Hooks:**
    - `HOOK_AFTER_USER_ROLE`: executes after the user role or active
      status has been updated.
    """
    config = request.app.state.config

    user_repository = Repository(session, cache, User, config)
    user = await user_repository.select(id=user_id)

    if not user:
        raise E([LOC_PATH, "user_id"], user_id,
                ERR_VALUE_NOT_FOUND, status.HTTP_404_NOT_FOUND)

    elif user_id == current_user.id:
        raise E([LOC_PATH, "user_id"], user_id,
                ERR_VALUE_INVALID, status.HTTP_422_UNPROCESSABLE_ENTITY)

    user.active = schema.active
    user.role = schema.role
    await user_repository.update(user)

    hook = Hook(request, session, cache, current_user=current_user)
    await hook.call(HOOK_AFTER_USER_ROLE, user)

    request.state.log.debug("user role changed; user_id=%s;", user.id)
    return {"user_id": user.id}
