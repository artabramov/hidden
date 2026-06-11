# app/middleware/mountpoint_check.py
# SPDX-License-Identifier: GPL-3.0-only

from fastapi import Request, status
from fastapi.responses import Response

from app.config import get_config
from app.repositories.file import isfile, ismount

MOUNTPOINT_CHECK_EXCLUDED_URLS = {
    "/docs",
    "/openapi.json",
}


async def mountpoint_check_middleware(request: Request, call_next):
    config = get_config()

    url = request.url.path.rstrip("/") or "/"
    init_prefix = f"/{config.API_PREFIX.strip('/')}/init/"

    if url.startswith(init_prefix) or url in MOUNTPOINT_CHECK_EXCLUDED_URLS:
        return await call_next(request)

    # Scenario 1: passphrase is missing
    if not await isfile(config.GOCRYPTFS_PASSPHRASE_ENCRYPTED_PATH):
        return Response(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            headers={"Retry-After": "300"},
        )

    # Scenario 2: mountpoint is not mounted
    if not await ismount(config.GOCRYPTFS_MOUNTPOINT):
        return Response(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            headers={"Retry-After": "300"},
        )

    return await call_next(request)
