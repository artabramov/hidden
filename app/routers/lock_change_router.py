from fastapi import APIRouter, Depends, status
from app.helpers.lock_helper import lock_enable, lock_disable
from fastapi.responses import JSONResponse
from app.models.user_model import User, UserRole
from app.schemas.lock_schemas import LockUpdateRequest, LockUpdateResponse
from app.auth import auth
from app.hooks import Hook
from app.database import get_session
from app.cache import get_cache
from app.constants import HOOK_ON_LOCK_CHANGE

router = APIRouter()


@router.put("/locked", summary="Change lock mode",
            response_class=JSONResponse, status_code=status.HTTP_200_OK,
            response_model=LockUpdateResponse, tags=["Lock"])
async def lock_change(
    schema: LockUpdateRequest,
    session=Depends(get_session), cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.admin))
) -> LockUpdateResponse:
    if schema.is_locked:
        await lock_enable()
        is_locked = True

    else:
        await lock_disable()
        is_locked = False

    hook = Hook(session, cache)
    await hook.do(HOOK_ON_LOCK_CHANGE, is_locked)

    return {"is_locked": is_locked}
