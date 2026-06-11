# app/handlers/too_many_requests.py
# SPDX-License-Identifier: GPL-3.0-only

from fastapi import Request, status
from fastapi.responses import JSONResponse

from app.errors import TooManyRequestsError


async def too_many_requests_handler(
    request: Request,
    exc: TooManyRequestsError,
) -> JSONResponse:
    """
    Handle rate limit violations by returning a 429 response.

    Used for registration and master-password attempt spacing, among
    other TooManyRequestsError sources.
    """
    return JSONResponse(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        content={"detail": "Too many requests"},
    )
