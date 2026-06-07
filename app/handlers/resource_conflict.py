# app/handlers/resource_conflict.py
# SPDX-License-Identifier: SSPL-1.0

from fastapi import Request, status
from fastapi.responses import Response

from app.errors import ResourceConflictError


async def resource_conflict_handler(
    request: Request,
    _exc: ResourceConflictError,
) -> Response:
    """
    Handle resource conflict errors by returning an empty 409 response.
    """
    return Response(status_code=status.HTTP_409_CONFLICT)
