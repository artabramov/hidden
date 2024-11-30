import time
from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from app.database import get_session
from app.cache import get_cache
from app.auth import auth
from app.models.user_model import User, UserRole
from app.decorators.locked_decorator import locked
import platform
import psutil
from app.managers.entity_manager import EntityManager
from app.version import __version__
from app.serial import __serial__
from app.hooks import Hook
from app.constants import HOOK_ON_TELEMETRY_RETRIEVE
from app.schemas.telemetry_schemas import TelemetryRetrieveResponse

router = APIRouter()


@router.get("/telemetry", summary="Retrieve telemetry data",
            response_class=JSONResponse, status_code=status.HTTP_200_OK,
            response_model=TelemetryRetrieveResponse,
            tags=["Telemetry"])
@locked
async def telemetry_retrieve(
    session=Depends(get_session), cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.admin))
):
    from app.app import uptime

    entity_manager = EntityManager(session)

    postgres_version = await entity_manager.select_rows("SELECT version();")
    postgres_database_size = await entity_manager.select_rows(
        "SELECT pg_size_pretty(pg_database_size(current_database()));")
    postgres_start_time = await entity_manager.select_rows(
        "SELECT pg_postmaster_start_time();")

    hook = Hook(session, cache, current_user=current_user)
    await hook.do(HOOK_ON_TELEMETRY_RETRIEVE)

    return {
        "unix_timestamp": int(time.time()),
        "timezone_name": time.tzname[0],
        "timezone_offset": time.timezone,

        "hidden_uptime": uptime.get_uptime(),
        "hidden_version": __version__,
        "hidden_serial": __serial__,

        "postgres_version": str(postgres_version[0][0]),
        "postgres_database_size": str(postgres_database_size[0][0]),
        "postgres_start_time": str(postgres_start_time[0][0]),

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
