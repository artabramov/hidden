from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from app.postgres import get_session
from app.redis import get_cache
from app.models.user_model import User, UserRole
from app.schemas.user_select_schema import UserSelectResponse
from app.error import E, LOC_PATH, ERR_VALUE_NOT_FOUND
from app.hook import Hook, HOOK_AFTER_USER_SELECT
from app.auth import auth
from app.repository import Repository

router = APIRouter()


@router.get("/user/{user_id}", summary="Retrieve a user.",
            response_class=JSONResponse, status_code=status.HTTP_200_OK,
            response_model=UserSelectResponse, tags=["Users"])
async def user_select(
    user_id: int,
    session=Depends(get_session), cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.reader))
) -> UserSelectResponse:
    """
    Retrieves a user. Fetches the user from the repository using the
    provided ID and returns the user details.

    **Auth:**
    - The token must be included in the request header and contain auth
    data for an active user with the `reader`, `writer`, `editor`, or
    `admin` role.

    **Returns:**
    - `UserSelectResponse`: User details on success.

    **Responses:**
    - `200 OK`: If the user is successfully retrieved.
    - `401 Unauthorized`: If the token is invalid or lacks permissions.
    - `403 Forbidden`: If the token or secret key is missing.
    - `404 Not Found`: If the user is not found.
    - `423 Locked`: If the app is locked.

    **Hooks:**
    - `HOOK_AFTER_USER_SELECT`: Executes after the user is successfully
    retrieved.
    """
    user_repository = Repository(session, cache, User)
    user = await user_repository.select(id=user_id)

    if not user:
        raise E([LOC_PATH, "user_id"], user_id,
                ERR_VALUE_NOT_FOUND, status.HTTP_404_NOT_FOUND)

    hook = Hook(session, cache, current_user=current_user)
    await hook.call(HOOK_AFTER_USER_SELECT, user)

    return await user.to_dict()
