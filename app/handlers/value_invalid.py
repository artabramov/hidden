# app/handlers/value_invalid.py
# SPDX-License-Identifier: GPL-3.0-only

from fastapi import Request, status
from fastapi.responses import JSONResponse

from app.errors import PydanticError


async def value_invalid_handler(
    request: Request,
    exc: PydanticError,
) -> JSONResponse:
    """
    Handle project-level validation errors by returning a 422 response
    with a Pydantic-like error detail payload.
    """
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.detail},
    )
