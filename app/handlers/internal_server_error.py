# app/handlers/internal_server_error.py
# SPDX-License-Identifier: SSPL-1.0

from fastapi import Request, status
from fastapi.responses import Response

from app.errors import InternalServerError


async def internal_server_error_handler(
    request: Request,
    exc: InternalServerError,
) -> Response:
    """
    Handle internal server errors by returning an empty 500 response.
    """
    return Response(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
