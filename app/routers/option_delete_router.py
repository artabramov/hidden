"""
The module defines a FastAPI router for deleting option entities.
"""

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from app.database import get_session
from app.cache import get_cache
from app.decorators.locked_decorator import locked
from app.models.user_model import User, UserRole
from app.models.option_model import Option
from app.schemas.option_schemas import OptionDeleteResponse
from app.repository import Repository
from app.hooks import Hook
from app.errors import E
from app.auth import auth
from app.constants import (
    LOC_PATH, ERR_RESOURCE_NOT_FOUND, HOOK_BEFORE_OPTION_DELETE,
    HOOK_AFTER_OPTION_DELETE)

router = APIRouter()


@router.delete("/option/{option_key}", summary="Delete an option.",
               response_class=JSONResponse, status_code=status.HTTP_200_OK,
               response_model=OptionDeleteResponse, tags=["Options"])
@locked
async def option_delete(
    option_key: str,
    session=Depends(get_session), cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.admin)),
) -> OptionDeleteResponse:
    """
    Delete an option. The router retrieves the option from the
    repository using the provided option key. If the option exists,
    it deletes it from the repository and executes related hooks. The
    router returns the option key of the deleted option in a JSON
    response. The current user should have an admin role. Returns a 200
    response on success, a 404 error if the option is not found, a 401
    error if authentication failed or the user does not have the
    required permissions, a 403 error if the token is missing, a 423
    error if the the application is locked.

    **Args:**
    - `option_key`: The key of the option to be deleted.

    **Returns:**
    - `OptionDeleteResponse`: The response schema containing the key of
    the deleted option.

    **Raises:**
    - `401 Unauthorized`: Raised if the token is invalid or expired,
    or if the current user is not authenticated or does not have the
    required permissions.
    - `403 Forbidden`: Raised if the token is missing.
    - `404 Not Found`: Raised if the option is not found in the
    repository.
    - `423 Locked`: Raised if the the application is locked.

    **Auth:**
    - The user must provide a valid `JWT token` in the request header.
    - `admin` role is required to access this router.
    """
    option_repository = Repository(session, cache, Option)
    option = await option_repository.select(option_key__eq=option_key)

    if not option:
        raise E([LOC_PATH, "option_key"], option_key,
                ERR_RESOURCE_NOT_FOUND, status.HTTP_404_NOT_FOUND)

    await option_repository.delete(option, commit=False)

    hook = Hook(session, cache, current_user=current_user)
    await hook.do(HOOK_BEFORE_OPTION_DELETE, option)

    await option_repository.commit()
    await hook.do(HOOK_AFTER_OPTION_DELETE, option)

    return {"option_key": option.option_key if option else None}
