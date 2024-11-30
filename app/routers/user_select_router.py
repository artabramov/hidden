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


@router.get("/user/{user_id}", summary="Retrieve user",
            response_class=JSONResponse, status_code=status.HTTP_200_OK,
            response_model=UserSelectResponse, tags=["Users"])
@locked
async def user_select(
    user_id: int,
    session=Depends(get_session), cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.reader))
) -> UserSelectResponse:
    """
    FastAPI router for retrieving a user entity. Returns a 200 response
    with the user's details if found. Raises a 404 error if the user is
    not found. Requires the user to have the reader role or higher.
    Returns a 403 error if the user's token is invalid or if the user
    does not have the required role.
    """
    user_repository = Repository(session, cache, User)
    user = await user_repository.select(id=user_id)

    if not user:
        raise E([LOC_PATH, "user_id"], user_id,
                ERR_RESOURCE_NOT_FOUND, status.HTTP_404_NOT_FOUND)

    hook = Hook(session, cache, current_user=user)
    await hook.do(HOOK_AFTER_USER_SELECT, user)

    return await user.to_dict()
