from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from app.database import get_session
from app.cache import get_cache
from app.decorators.locked_decorator import locked
from app.models.user_model import User, UserRole
from app.models.option_model import Option
from app.schemas.option_schemas import (
    OptionUpdateRequest, OptionUpdateResponse, OptionInsertRequest)
from app.repository import Repository
from app.hooks import Hook
from app.auth import auth
from app.errors import E
from app.constants import (
    LOC_PATH, ERR_VALUE_INVALID, HOOK_BEFORE_OPTION_UPDATE,
    HOOK_AFTER_OPTION_UPDATE)

router = APIRouter()


@router.put("/option/{option_key}", summary="Update an option.",
            response_class=JSONResponse, status_code=status.HTTP_200_OK,
            response_model=OptionUpdateResponse, tags=["Options"])
@locked
async def option_update(
    option_key: str, schema: OptionUpdateRequest,
    session=Depends(get_session), cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.admin)),
) -> OptionUpdateResponse:
    """
    Update an option. The router retrieves the option from the
    repository using the provided option key. If the option exists, it
    updates the option value, otherwise, it creates a new option. The
    router executes related hooks before and after the option update.
    The current user should have an admin role. Returns a 200 response
    on success, a 403 error if authentication failed or the user does
    not have the required permissions, a 422 error if the provided
    option value is invalid, and a 423 error if the application is
    locked.

    **Args:**
    - `option_key`: The key of the option to update.
    - `OptionUpdateRequest`: The request schema containing the updated
      option value.

    **Returns:**
    - `OptionUpdateResponse`: The response schema containing the updated 
      option key.

    **Raises:**
    - `403 Forbidden`: Raised if the user does not have the required 
      permissions.
    - `422 Unprocessable Entity`: Raised if the provided option value 
      is invalid.
    - `423 Locked`: Raised if the application is locked.

    **Auth:**
    - The user must provide a valid `JWT token` in the request header.
    - `admin` role is required to access this router.
    """
    option_repository = Repository(session, cache, Option)
    option = await option_repository.select(option_key__eq=option_key)

    try:
        OptionInsertRequest(option_key=option_key,
                            option_value=schema.option_value)
    except ValidationError:
        raise E([LOC_PATH, "option_key"], option_key,
                ERR_VALUE_INVALID, status.HTTP_422_UNPROCESSABLE_ENTITY)

    if not option:
        option = Option(current_user.id, option_key, schema.option_value)
        await option_repository.insert(option, commit=False)

    else:
        option.option_value = schema.option_value
        await option_repository.update(option, commit=False)

    hook = Hook(session, cache, current_user=current_user)
    await hook.do(HOOK_BEFORE_OPTION_UPDATE, option)

    await option_repository.commit()
    await hook.do(HOOK_AFTER_OPTION_UPDATE, option)

    return {"option_key": option.option_key if option else None}
