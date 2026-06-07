# app/handlers/resource_not_found.py
# SPDX-License-Identifier: SSPL-1.0

from fastapi import Request, status
from fastapi.responses import Response

from app.errors import ResourceNotFoundError


async def resource_not_found_handler(
    request: Request,
    exc: ResourceNotFoundError,
) -> Response:
    """
    Handle missing resources by returning an empty 404 response.
    """
    return Response(status_code=status.HTTP_404_NOT_FOUND)
