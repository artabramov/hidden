"""
The module defines a FastAPI router for retrieving the option list.
"""

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from app.database import get_session
from app.cache import get_cache
from app.decorators.locked_decorator import locked
from app.models.user_model import User, UserRole
from app.models.option_model import Option
from app.schemas.option_schemas import OptionListRequest, OptionListResponse
from app.repository import Repository
from app.hooks import Hook
from app.auth import auth
from app.constants import HOOK_AFTER_OPTION_LIST

router = APIRouter()


@router.get("/options", summary="Fetch option list",
            response_class=JSONResponse, status_code=status.HTTP_200_OK,
            response_model=OptionListResponse, tags=["Options"])
@locked
async def options_list(
    schema=Depends(OptionListRequest),
    session=Depends(get_session), cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.admin))
) -> OptionListResponse:
    """
    FastAPI router for retrieving a list of option entities. The router
    retrieves all options from the repository based on the provided
    filter criteria and executes related hooks. The router returns a
    list of options and the total count of options in a JSON response.
    The current user should have an admin role. Returns a 200 response
    on success and a 403 error if authentication fails or the user does
    not have the required role.
    """
    option_repository = Repository(session, cache, Option)

    options = await option_repository.select_all(**schema.__dict__)
    options_count = await option_repository.count_all(**schema.__dict__)

    hook = Hook(session, cache, current_user=current_user)
    await hook.do(HOOK_AFTER_OPTION_LIST, options)

    return {
        "options": [await option.to_dict() for option in options],
        "options_count": options_count,
    }
