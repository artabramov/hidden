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


@router.get("/users", summary="Retrieve user list",
            response_class=JSONResponse, status_code=status.HTTP_200_OK,
            response_model=UserListResponse, tags=["Users"])
@locked
async def users_list(
    schema=Depends(UserListRequest),
    session=Depends(get_session), cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.reader))
) -> UserListResponse:
    """
    FastAPI router for retrieving a list of user entities. Requires the
    user to have a reader role or higher. Returns a 200 response with
    the list of users and the total count. Raises a 403 error if the
    user's token is invalid or if the user does not have the required
    role. Raises a 422 error if any query parameters are invalid.
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
