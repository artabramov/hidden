# app/handlers/value_not_found.py
# SPDX-License-Identifier: SSPL-1.0

from fastapi import Request, status
from fastapi.responses import JSONResponse

from app.errors import PydanticError


async def value_not_found_handler(
    request: Request,
    exc: PydanticError,
) -> JSONResponse:
    """
    Handle value-not-found errors by returning a 422 response with
    a Pydantic-like error detail payload.
    """
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.detail},
    )
