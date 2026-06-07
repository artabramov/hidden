# app/middleware/lockdown_mode.py
# SPDX-License-Identifier: SSPL-1.0

from fastapi import Request, status
from starlette.responses import Response

from app.config import get_config
from app.constants import LOCKDOWN_MODE_ENABLED_FLAG_PATH
from app.repositories.file import isfile

LOCKDOWN_MODE_EXCLUDED_URLS = {
    "/docs",
    "/openapi.json",
}


async def lockdown_mode_middleware(request: Request, call_next):
    """
    Enforces lockdown mode when the flag file is present (503).
    Blocks all requests except init and explicitly excluded paths.
    """
    config = get_config()

    if not await isfile(LOCKDOWN_MODE_ENABLED_FLAG_PATH):
        return await call_next(request)

    init_prefix = f"/{config.API_PREFIX.strip('/')}/init/"
    url = request.url.path.rstrip("/") or "/"

    if url.startswith(init_prefix) or url in LOCKDOWN_MODE_EXCLUDED_URLS:
        return await call_next(request)

    return Response(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        headers={"Retry-After": "300"},
    )
