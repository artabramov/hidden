import time
from fastapi import APIRouter, Depends, status, Request
from fastapi.responses import JSONResponse
from app.postgres import get_session
from app.redis import get_cache
from app.config import get_config
from app.auth import auth
from app.models.user_model import User, UserRole
import platform
import psutil
from app.managers.entity_manager import EntityManager
from app.version import __version__
from app.hook import Hook, HOOK_AFTER_TELEMETRY_RETRIEVE
from app.schemas.telemetry_retrieve_schema import TelemetryRetrieveResponse

cfg = get_config()
router = APIRouter()


@router.get("/telemetry", summary="Retrieve telemetry.",
            response_class=JSONResponse, status_code=status.HTTP_200_OK,
            response_model=TelemetryRetrieveResponse,
            tags=["Services"])
async def telemetry_retrieve(
    request: Request,
    session=Depends(get_session), cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.admin))
):
    """
    Retrieves telemetry. Aggregates system metrics and configuration
    details.

    **Auth:**
    - The token must be included in the request header and contain auth
    data for an active user with the `admin` role.

    **Returns:**
    - `UserSelectResponse`: Telemetry details on success.

    **Raises:**
    - `200 OK`: If telemetry is successfully retrieved.
    - `401 Unauthorized`: If the token is invalid or lacks permissions.
    - `403 Forbidden`: If the token or secret key is missing.
    - `423 Locked`: If the app is locked.

    **Hooks:**
    - `HOOK_AFTER_TELEMETRY_RETRIEVE`: Executes after telemetry is
    successfully retrieved.
    """
    from app.app import uptime
    from serial import __serial__

    entity_manager = EntityManager(session)
    postgres_version = await entity_manager.select_rows("SHOW server_version;")
    postgres_size = await entity_manager.select_rows(
        "SELECT pg_database_size(current_database());")

    redis_server = await cache.info("server")
    redis_memory = await cache.info("memory")

    telemetry = {
        "app_version": __version__,
        "app_serial": __serial__,
        "app_uptime": uptime.get_uptime(),

        "unix_timestamp": int(time.time()),
        "timezone_name": time.tzname[0],
        "timezone_offset": time.timezone,

        "postgres_version": str(postgres_version[0][0].split()[0]),
        "postgres_size": int(postgres_size[0][0]),

        "redis_version": redis_server["redis_version"],
        "redis_mode": redis_server["redis_mode"],
        "redis_memory": redis_memory["used_memory"],

        "platform_architecture": platform.architecture()[0],
        "platform_machine": platform.machine(),
        "platform_node": platform.node(),
        "platform_alias": platform.platform(aliased=True),
        "platform_processor": platform.processor(),

        "python_buildno": platform.python_build()[0],
        "python_builddate": platform.python_build()[1],
        "python_compiler": platform.python_compiler(),
        "python_branch": platform.python_branch(),
        "python_implementation": platform.python_implementation(),
        "python_revision": platform.python_revision(),
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

    hook = Hook(request.app, session, cache, current_user=current_user)
    await hook.call(HOOK_AFTER_TELEMETRY_RETRIEVE, telemetry)

    return telemetry
