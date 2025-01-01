from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from app.database import get_session
from app.cache import get_cache
from app.decorators.locked_decorator import locked
from app.models.user_model import User, UserRole
from app.schemas.user_schemas import UserListRequest, UserListResponse
from app.hooks import Hook
from app.auth import auth
from app.repository import Repository
from app.constants import HOOK_AFTER_USER_LIST

router = APIRouter()


@router.get("/users", summary="Retrieve a list of users.",
            response_class=JSONResponse, status_code=status.HTTP_200_OK,
            response_model=UserListResponse, tags=["Users"])
@locked
async def users_list(
    schema=Depends(UserListRequest),
    session=Depends(get_session), cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.reader))
) -> UserListResponse:
    """
    Retrieve a list of users. This endpoint fetches all users from
    the repository based on the provided filter criteria and executes
    related hooks. The current user must have a reader role or higher.
    Returns a 200 response on success, a 401 error if authentication
    failed or the user does not have the required permissions, a 403
    error if the token is missing, a 422 error if arguments validation
    failed, and a 423 error if the application is locked.

    **Returns:**
    - `UserListResponse`: A response schema containing the list of users
    and the total count.

    **Raises:**
    - `401 Unauthorized`: Raised if the token is invalid or expired,
    or if the current user is not authenticated or does not have the
    required permissions.
    - `403 Forbidden`: Raised if the token is missing.
    - `422 Unprocessable Entity`: Raised if the arguments in the request
    schema are invalid.
    - `423 Locked`: Raised if the application is locked.

    **Hooks:**
    - `HOOK_AFTER_USER_LIST`: Executes after the user list is retrieved.

    **Auth:**
    - The user must provide a valid `JWT token` in the request header.
    - The `reader`, `writer`, `editor`, or `admin` role is required to
    access this router.
    """
    user_repository = Repository(session, cache, User)

    users = await user_repository.select_all(**schema.__dict__)
    users_count = await user_repository.count_all(**schema.__dict__)

    hook = Hook(session, cache, current_user=current_user)
    await hook.do(HOOK_AFTER_USER_LIST, users)

    return {
        "users": [await user.to_dict() for user in users],
        "users_count": users_count,
    }
