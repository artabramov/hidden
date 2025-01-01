import time
from fastapi import APIRouter, status, Depends
from fastapi.responses import JSONResponse
from app.schemas.heartbeat_schemas import HeartbeatRetrieveResponse
from app.hooks import Hook
from app.helpers.lock_helper import is_locked, locked_date
from app.database import get_session
from app.cache import get_cache
from app.constants import HOOK_ON_HEARTBEAT_RETRIEVE

router = APIRouter()


@router.get("/heartbeat", summary="Retrieve a heartbeat.",
            response_class=JSONResponse, status_code=status.HTTP_200_OK,
            response_model=HeartbeatRetrieveResponse,
            tags=["Services"])
async def heartbeat_retrieve(
    session=Depends(get_session), cache=Depends(get_cache)
) -> HeartbeatRetrieveResponse:
    """
    Retrieve a heartbeat data. It executes a corresponding hook after
    retrieving the data.

    **Returns:**
    - `HeartbeatRetrieveResponse`: The response schema containing the
    Unix timestamp, timezone data, lock status and the date when the
    application was locked.

    **Auth:**
    - No authentication is required to access this router.
    """
    locked = is_locked()

    hook = Hook(session, cache)
    await hook.do(HOOK_ON_HEARTBEAT_RETRIEVE, locked)

    return {
        "unix_timestamp": int(time.time()),
        "timezone_name": time.tzname[0],
        "timezone_offset": time.timezone,
        "is_locked": locked,
        "locked_date": locked_date(),
    }
