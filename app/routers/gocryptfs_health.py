# app/routers/gocryptfs_health.py
# SPDX-License-Identifier: Apache-2.0

from fastapi import APIRouter, status

from app.schemas.gocryptfs_health import GocryptfsHealthResponse
from app.services.gocryptfs_health import gocryptfs_health

router = APIRouter(tags=["gocryptfs"])


@router.get(
    "/gocryptfs/health",
    responses={},
    response_model=GocryptfsHealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Retrieve gocryptfs runtime state.",
)
async def gocryptfs_health_router() -> GocryptfsHealthResponse:
    """
    Returns the current gocryptfs runtime state for polling: whether
    the cipherdir is initialized, whether it is mounted, whether the
    watchdog heartbeat is alive, and basic local time metadata.

    Always returns HTTP 200 with a snapshot body. Clients should poll
    this endpoint and inspect the boolean fields rather than treating
    non-ready state as an HTTP error.
    """
    health = await gocryptfs_health()
    return GocryptfsHealthResponse(**health)
