from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from app.postgres import get_session
from app.redis import get_cache
from app.models.user_model import User, UserRole
from app.schemas.user_role_schema import UserRoleRequest, UserRoleResponse
from app.error import E, ERR_VALUE_NOT_FOUND, ERR_VALUE_ERROR, LOC_PATH
from app.hook import Hook, HOOK_AFTER_USER_ROLE
from app.auth import auth
from app.repository import Repository

router = APIRouter()


@router.put("/user/{user_id}/role", summary="Change a user role.",
            response_class=JSONResponse, status_code=status.HTTP_200_OK,
            response_model=UserRoleResponse, tags=["Users"])
async def user_role(
    user_id: int, schema: UserRoleRequest,
    session=Depends(get_session), cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.admin))
) -> UserRoleResponse:
    """
    Changes a role and activity status of a user. Fetches the user from
    the repository using the provided ID and changes its activity status
    and role. The current user cannot update their own role or activity
    status.

    **Auth:**
    - The token must be included in the request header and contain auth
    data for an active user with the `admin` role.

    **Returns:**
    - `UserRoleResponse`: Contains the ID of the updated user.

    **Responses:**
    - `200 OK`: If the user role is successfully updated.
    - `401 Unauthorized`: If the token is invalid or lacks permissions.
    - `403 Forbidden`: If the token or secret key is missing.
    - `404 Not Found`: If the user is not found.
    - `422 Unprocessable Entity`: If parameters validation fails.
    - `423 Locked`: If the app is locked.

    **Hooks:**
    - `HOOK_AFTER_USER_ROLE`: Executes after the role and activity
    status are successfully changed.
    """
    user_repository = Repository(session, cache, User)
    user = await user_repository.select(id=user_id)

    if not user:
        raise E([LOC_PATH, "user_id"], user_id,
                ERR_VALUE_NOT_FOUND, status.HTTP_404_NOT_FOUND)

    elif user_id == current_user.id:
        raise E([LOC_PATH, "user_id"], user_id,
                ERR_VALUE_ERROR, status.HTTP_422_UNPROCESSABLE_ENTITY)

    user.is_active = schema.is_active
    user.user_role = schema.user_role
    await user_repository.update(user)

    hook = Hook(session, cache, current_user=current_user)
    await hook.call(HOOK_AFTER_USER_ROLE, user)

    return {"user_id": user.id}
