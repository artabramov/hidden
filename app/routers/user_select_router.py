from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from app.database import get_session
from app.cache import get_cache
from app.decorators.locked_decorator import locked
from app.models.user_model import User, UserRole
from app.schemas.user_schemas import UserSelectResponse
from app.errors import E
from app.hooks import Hook
from app.auth import auth
from app.repository import Repository
from app.constants import (
    LOC_PATH, ERR_RESOURCE_NOT_FOUND, HOOK_AFTER_USER_SELECT)

router = APIRouter()


@router.get("/user/{user_id}", summary="Retrieve a user.",
            response_class=JSONResponse, status_code=status.HTTP_200_OK,
            response_model=UserSelectResponse, tags=["Users"])
@locked
async def user_select(
    user_id: int,
    session=Depends(get_session), cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.reader))
) -> UserSelectResponse:
    """
    Retrieve a user. The router fetches the user from the repository
    using the provided ID, executes related hooks, and returns the user
    details in a JSON response. Requires the user to have the reader
    role or higher. Returns a 200 response with the user's details if
    found. Raises a 404 error if the user is not found, a 401 error if
    the user's token is invalid or if the user does not have the
    required role, a 403 error if the token is missing, a 423 error
    if the application is locked.

    **Returns:**
    - `UserSelectResponse`: A response schema containing the details of
    the retrieved user.

    **Raises:**
    - `401 Unauthorized`: Raised if the token is invalid or expired,
    or if the current user is not authenticated or does not have the
    required permissions.
    - `403 Forbidden`: Raised if the token is missing.
    - `404 Not Found`: Raised if the user with the given ID is not found.
    - `423 Locked`: Raised if the application is locked.

    **Hooks:**
    - `HOOK_AFTER_USER_SELECT`: Executes after successfully retrieving
    the user.

    **Auth:**
    - The user must provide a valid `JWT token` in the request header.
    - The `reader`, `writer`, `editor`, or `admin` role is required to
    access this router.
    """
    user_repository = Repository(session, cache, User)
    user = await user_repository.select(id=user_id)

    if not user:
        raise E([LOC_PATH, "user_id"], user_id,
                ERR_RESOURCE_NOT_FOUND, status.HTTP_404_NOT_FOUND)

    hook = Hook(session, cache, current_user=user)
    await hook.do(HOOK_AFTER_USER_SELECT, user)

    return await user.to_dict()
