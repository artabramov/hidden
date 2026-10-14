# app/handlers.py
# SPDX-License-Identifier: Apache-2.0

from fastapi import Request, status
from fastapi.responses import Response

from app.errors import (
    UnauthorizedError,
    InternalServerError,
    ServiceUnavailableError,
    BadGatewayError,
)


async def unauthorized_handler(
    request: Request,
    exc: UnauthorizedError,
) -> Response:
    return Response(status_code=status.HTTP_401_UNAUTHORIZED)


async def internal_server_error_handler(
    request: Request,
    exc: InternalServerError,
) -> Response:
    return Response(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


async def bad_gateway_handler(
    request: Request,
    exc: BadGatewayError,
) -> Response:
    return Response(status_code=status.HTTP_502_BAD_GATEWAY)


async def service_unavailable_handler(
    request: Request,
    exc: ServiceUnavailableError,
) -> Response:
    return Response(status_code=status.HTTP_503_SERVICE_UNAVAILABLE)
