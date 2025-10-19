"""FastAPI router for retrieving telemetry."""

import time
from fastapi import Request, APIRouter, Depends, status
from fastapi.responses import JSONResponse
from app.sqlite import get_session
from app.redis import get_cache
from app.auth import auth
from app.models.user import User, UserRole
import platform
import psutil
from app.managers.entity_manager import EntityManager
from app.version import __version__
from app.schemas.telemetry_retrieve import TelemetryRetrieveResponse
from app.hook import Hook, HOOK_AFTER_TELEMETRY_RETRIEVE

router = APIRouter()


@router.get(
    "/telemetry",
    status_code=status.HTTP_200_OK,
    response_class=JSONResponse,
    response_model=TelemetryRetrieveResponse,
    summary="Retrieve telemetry.",
    tags=["Telemetry"]
)
async def telemetry_retrieve(
    request: Request,
    session=Depends(get_session),
    cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.admin))
):
    """
    Retrieves telemetry. Aggregates system metrics and configuration
    details.

    **Auth:**
    - The token must be included in the request header and contain auth
    data for an active user with the `admin` role.

    **Returns:**
    - `TelemetryRetrieveResponse`: Telemetry details on success.

    **Raises:**
    - `200 OK`: If telemetry is successfully retrieved.
    - `401` — missing, invalid, or expired token.
    - `403` — insufficient role, invalid JTI, user is inactive or
    suspended.
    - `423` — application is temporarily locked.
    - `498` — gocryptfs key is missing.
    - `499` — gocryptfs key is invalid.

    **Hooks:**
    - `HOOK_AFTER_TELEMETRY_RETRIEVE`: Executes after telemetry is
    successfully retrieved.
    """
    entity_manager = EntityManager(session)
    sqlite_version = await entity_manager.select_rows(
        "SELECT sqlite_version();"
    )
    sqlite_size = await entity_manager.select_rows(
        "SELECT (pc.page_count * ps.page_size) AS database_size "
        "FROM pragma_page_count AS pc, pragma_page_size AS ps;"
    )

    redis_server = await cache.info("server")
    redis_memory = await cache.info("memory")

    telemetry = {
        "app_version": __version__,
        "unix_timestamp": int(time.time()),
        "timezone_name": time.tzname[0],
        "timezone_offset": time.timezone,
        "sqlite_version": str(sqlite_version[0][0].split()[0]),
        "sqlite_size": int(sqlite_size[0][0]),
        "redis_version": redis_server["redis_version"],
        "redis_memory": redis_memory["used_memory"],
        "platform_alias": platform.platform(aliased=True),
        "platform_architecture": platform.architecture()[0],
        "platform_processor": platform.processor(),
        "python_compiler": platform.python_compiler(),
        "python_implementation": platform.python_implementation(),
        "python_version": platform.python_version(),
        "os_name": platform.system(),
        "os_release": platform.release(),
        "os_version": platform.version(),
        "disk_total": psutil.disk_usage("/").total,
        "disk_used": psutil.disk_usage("/").used,
        "disk_free": psutil.disk_usage("/").free,
        "memory_total": psutil.virtual_memory().total,
        "memory_used": psutil.virtual_memory().used,
        "memory_free": psutil.virtual_memory().free,
        "cpu_core_count": psutil.cpu_count(logical=False),
        "cpu_frequency": int(psutil.cpu_freq(percpu=False).current) * 1000000,
        "cpu_usage_percent": psutil.cpu_percent(),
    }

    hook = Hook(request, session, cache, current_user=current_user)
    await hook.call(HOOK_AFTER_TELEMETRY_RETRIEVE, telemetry)

    return telemetry
