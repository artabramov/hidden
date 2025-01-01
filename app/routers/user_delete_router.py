"""
The module defines a FastAPI router for deleting user entities.
"""

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from app.database import get_session
from app.cache import get_cache
from app.decorators.locked_decorator import locked
from app.models.user_model import User, UserRole
from app.schemas.user_schemas import UserDeleteResponse
from app.repository import Repository
from app.errors import E
from app.hooks import Hook
from app.auth import auth
from app.constants import (
    LOC_PATH, ERR_RESOURCE_NOT_FOUND, ERR_RESOURCE_FORBIDDEN,
    HOOK_BEFORE_USER_DELETE, HOOK_AFTER_USER_DELETE)

router = APIRouter()


@router.delete("/user/{user_id}", summary="Delete a user.",
               response_class=JSONResponse, status_code=status.HTTP_200_OK,
               response_model=UserDeleteResponse, tags=["Users"])
@locked
async def user_delete(
    user_id: int,
    session=Depends(get_session), cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.admin)),
) -> UserDeleteResponse:
    """
    Delete a user. The router checks if the current user is not trying
    to delete their own account, retrieves the user from the repository
    using the provided ID, verifies if the user exists, deletes the user,
    and executes related hooks. The current user should have an admin
    role. Returns a 200 response on success, a 401 error if the current
    user attempts to delete their own account or if an exception occurs
    during deletion, a 403 error if the token is missing, a 404 error if
    the user is not found, and a 423 error if the application is locked.

    **Returns:**
    - `UserDeleteResponse`: The ID of the user to delete.

    **Raises:**
    - `401 Unauthorized`: Raised if the token is invalid or expired,
    or if the current user is not authenticated or does not have the
    required permissions.
    - `403 Forbidden`: Raised if the token is missing.
    - `404 Not Found`: Raised if the user with the provided ID does not
    exist.
    - `423 Locked`: Raised if the application is locked.

    **Hooks:**
    - `HOOK_BEFORE_USER_DELETE`: Executes before deleting the user.
    - `HOOK_AFTER_USER_DELETE`: Executes after the user has been deleted.

    **Auth:**
    - The user must provide a valid `JWT token` in the request header.
    - The `admin` role is required to access this router.
    """
    if user_id == current_user.id:
        raise E([LOC_PATH, "user_id"], user_id,
                ERR_RESOURCE_FORBIDDEN, status.HTTP_403_FORBIDDEN)

    user_repository = Repository(session, cache, User)
    user = await user_repository.select(id=user_id)

    if not user:
        raise E([LOC_PATH, "user_id"], user_id,
                ERR_RESOURCE_NOT_FOUND, status.HTTP_404_NOT_FOUND)

    elif user.last_login_date > 0:
        raise E([LOC_PATH, "user_id"], user_id,
                ERR_RESOURCE_FORBIDDEN, status.HTTP_403_FORBIDDEN)

    await user_repository.delete(user, commit=False)

    hook = Hook(session, cache, current_user=current_user)
    await hook.do(HOOK_BEFORE_USER_DELETE, user)

    await user_repository.commit()
    await hook.do(HOOK_AFTER_USER_DELETE, user)

    return {"user_id": user.id}
