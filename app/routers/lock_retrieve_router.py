from fastapi import APIRouter, status, Depends
from fastapi.responses import JSONResponse
from app.schemas.lock_schemas import LockRetrieveResponse
from app.hooks import Hook
from app.helpers.lock_helper import is_locked, locked_date
from app.database import get_session
from app.cache import get_cache
from app.constants import HOOK_ON_LOCK_RETRIEVE

router = APIRouter()


@router.get("/locked", summary="Retrieve the application lock mode.",
            response_class=JSONResponse, status_code=status.HTTP_200_OK,
            response_model=LockRetrieveResponse,
            tags=["Lock"])
async def lock_retrieve(
    session=Depends(get_session), cache=Depends(get_cache)
) -> LockRetrieveResponse:
    """
    Retrieve the application lock mode. This router checks whether the
    application is locked and retrieves the date when the lock was
    applied. It executes a corresponding hook after retrieving the lock
    state.

    **Returns:**
    - `LockRetrieveResponse`: The response schema containing the lock
    status and the date when the application was locked.

    **Auth:**
    - No authentication is required to access this router.
    """
    locked = is_locked()

    hook = Hook(session, cache)
    await hook.do(HOOK_ON_LOCK_RETRIEVE, locked)

    return {
        "is_locked": locked,
        "locked_date": locked_date(),
    }
