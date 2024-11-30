"""
The module defines a FastAPI router for retrieving option entities.
"""

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from app.database import get_session
from app.cache import get_cache
from app.decorators.locked_decorator import locked
from app.models.user_model import User, UserRole
from app.models.option_model import Option
from app.schemas.option_schemas import OptionSelectResponse
from app.repository import Repository
from app.errors import E
from app.hooks import Hook
from app.auth import auth
from app.constants import (
    LOC_PATH, ERR_RESOURCE_NOT_FOUND, HOOK_AFTER_OPTION_SELECT)

router = APIRouter()


@router.get("/option/{option_key}", summary="Get option",
            response_class=JSONResponse, status_code=status.HTTP_200_OK,
            response_model=OptionSelectResponse, tags=["Options"])
@locked
async def option_select(
    option_key: str,
    session=Depends(get_session), cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.admin))
) -> OptionSelectResponse:
    """
    FastAPI router for fetching an option entity. The router retrieves
    the option from the repository using the provided option key and
    executes related hooks. The current user should have an admin role.
    Returns a 200 response on success, a 404 error if the option is not
    found, and a 403 error if authentication fails or the user does
    not have the required role.
    """
    option_repository = Repository(session, cache, Option)
    option = await option_repository.select(option_key__eq=option_key)

    if not option:
        raise E([LOC_PATH, "option_key"], option_key,
                ERR_RESOURCE_NOT_FOUND, status.HTTP_404_NOT_FOUND)

    hook = Hook(session, cache, current_user=current_user)
    await hook.do(HOOK_AFTER_OPTION_SELECT, option)

    return await option.to_dict()
