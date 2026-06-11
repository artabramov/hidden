# app/handlers/service_unavailable.py
# SPDX-License-Identifier: GPL-3.0-only

from fastapi import Request, status
from fastapi.responses import Response

from app.errors import ServiceUnavailableError

# TODO: Add constant for Retry-After value.


async def service_unavailable_handler(
    request: Request,
    exc: ServiceUnavailableError,
) -> Response:
    """
    Handle service unavailability by returning a 503 response
    with a Retry-After header.
    """
    return Response(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        headers={"Retry-After": "300"}
    )
