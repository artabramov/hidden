# app/routers/metrics_retrieve.py
# SPDX-License-Identifier: SSPL-1.0

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.auth import AccessLevel, require_access
from app.dependencies.session import get_session
from app.models.user import User
from app.schemas.metrics_retrieve import METRICS_RETRIEVE_ERRORS
from app.services.metrics_retrieve import retrieve_metrics

router = APIRouter(tags=["Services"])


@router.get(
    "/metrics",
    responses=METRICS_RETRIEVE_ERRORS,
    status_code=status.HTTP_200_OK,
    summary="Getting metrics data",
)
async def retrieve_metrics_router(
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_access(AccessLevel.ADMIN)),
) -> JSONResponse:
    """
    Returns application metrics and runtime statistics.
    The response includes application version, platform details,
    Python runtime information, disk usage, memory usage, and CPU
    statistics.

    **Authentication:**

    - Requires a valid token with admin access.

    **Response codes:**

    - `200` — Metrics were returned successfully.
    """
    metrics = await retrieve_metrics(session)
    return JSONResponse(content=metrics)
