from fastapi import APIRouter, Depends, status, Request
from fastapi.responses import JSONResponse
from app.postgres import get_session
from app.redis import get_cache
from app.models.user_model import User, UserRole
from app.schemas.user_list_schema import UserListRequest, UserListResponse
from app.hook import Hook, HOOK_AFTER_USER_LIST
from app.auth import auth
from app.repository import Repository

router = APIRouter()


@router.get("/users", summary="Retrieve a list of users.",
            response_class=JSONResponse, status_code=status.HTTP_200_OK,
            response_model=UserListResponse, tags=["Users"])
async def user_list(
    request: Request, schema=Depends(UserListRequest),
    session=Depends(get_session), cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.reader))
) -> UserListResponse:
    """
    Retrieves a list of users. Fetches users from the repository based
    on the provided filter criteria, and includes a counter field to
    indicate the total number of matching users.

    **Auth:**
    - The token must be included in the request header and contain auth
    data for an active user with the `reader`, `writer`, `editor`, or
    `admin` role.

    **Returns:**
    - `UserListResponse`: Contains the list of users and the total count.

    **Responses:**
    - `200 OK`: If the users are successfully fetched.
    - `401 Unauthorized`: If the token is invalid or lacks permissions.
    - `403 Forbidden`: If the token or secret key is missing.
    - `423 Locked`: If the app is locked.

    **Hooks:**
    - `HOOK_AFTER_USER_LIST`: Executes after the users are successfully
    fetched.
    """
    user_repository = Repository(session, cache, User)

    users = await user_repository.select_all(**schema.__dict__)
    users_count = await user_repository.count_all(**schema.__dict__)

    hook = Hook(request.app, session, cache, current_user=current_user)
    await hook.call(HOOK_AFTER_USER_LIST, users, users_count)

    return {
        "users": [await user.to_dict() for user in users],
        "users_count": users_count,
    }
