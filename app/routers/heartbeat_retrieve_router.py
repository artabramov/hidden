from fastapi import APIRouter, status, Depends
import time
from fastapi.responses import JSONResponse
from app.schemas.heartbeat_schemas import HeartbeatRetrieveResponse
from app.hooks import Hook
from app.helpers.lock_helper import is_locked, get_locked_date
from app.database import get_session
from app.cache import get_cache
from app.constants import HOOK_ON_HEARTBEAT_RETRIEVE

router = APIRouter()


@router.get("/heartbeat", summary="Retrieve heartbeat",
            response_class=JSONResponse, status_code=status.HTTP_200_OK,
            response_model=HeartbeatRetrieveResponse, tags=["Services"])
async def time_retrieve(
    session=Depends(get_session), cache=Depends(get_cache)
) -> HeartbeatRetrieveResponse:

    hook = Hook(session, cache)
    await hook.do(HOOK_ON_HEARTBEAT_RETRIEVE)

    return {
        "unix_timestamp": int(time.time()),
        "timezone_name": time.tzname[0],
        "timezone_offset": time.timezone,
        "is_locked": is_locked(),
        "locked_date": get_locked_date(),
    }
