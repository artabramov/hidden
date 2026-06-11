# app/routers/health_check.py
# SPDX-License-Identifier: GPL-3.0-only

from fastapi import APIRouter, status
from fastapi.responses import JSONResponse

from app.services.health_check import health_check

router = APIRouter(tags=["Initialization"])


@router.get(
    "/init/health",
    status_code=status.HTTP_200_OK,
    summary="Health check",
)
async def health_check_router() -> JSONResponse:
    """
    Returns the current readiness state of the system. The response
    includes initialization status of encrypted storage, mount status,
    lockdown status, first-admin bootstrap status, watchdog status,
    and basic time metadata.

    **Authentication:**

    - Authentication is not required.

    **Response codes:**

    - `200` — Current system state was returned successfully.
    """
    health = await health_check()
    return JSONResponse(content=health)
