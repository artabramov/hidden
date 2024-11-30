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


@router.put("/option/{option_key}", summary="Update an option",
            response_class=JSONResponse, status_code=status.HTTP_200_OK,
            response_model=OptionUpdateResponse, tags=["Options"])
@locked
async def option_update(
    option_key: str, schema: OptionUpdateRequest,
    session=Depends(get_session), cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.admin)),
) -> OptionUpdateResponse:
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
