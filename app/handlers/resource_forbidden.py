# app/handlers/resource_forbidden.py
# SPDX-License-Identifier: GPL-3.0-only

from fastapi import Request, status
from fastapi.responses import Response

from app.errors import ResourceForbiddenError


async def resource_forbidden_handler(
    request: Request,
    exc: ResourceForbiddenError,
) -> Response:
    """
    Handle forbidden resource access by returning an empty 403 response.
    """
    return Response(status_code=status.HTTP_403_FORBIDDEN)
