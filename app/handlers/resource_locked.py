# app/handlers/resource_locked.py
# SPDX-License-Identifier: SSPL-1.0

from fastapi import Request, status
from fastapi.responses import Response

from app.errors import ResourceLockedError


async def resource_locked_handler(
    request: Request,
    exc: ResourceLockedError,
) -> Response:
    """
    Handle locked resource access by returning an empty 423 response.
    """
    return Response(status_code=status.HTTP_423_LOCKED)
