# app/middleware/request_context.py
# SPDX-License-Identifier: SSPL-1.0

import re
import time
import uuid

from fastapi import Request

from app.context import reset_context, set_context_var

# NOTE (ADR-20): X-Request-ID is accepted for request correlation.
# If not provided, a value is generated and returned in the response.

_REQUEST_UUID_MAX_LENGTH = 64
_REQUEST_UUID_RE = re.compile(
    rf"^[A-Za-z0-9_-]{{1,{_REQUEST_UUID_MAX_LENGTH}}}$",
)


def resolve_request_uuid(header_value: str | None) -> str:
    """
    Return a valid request correlation id. Uses the provided header
    value when it is valid, otherwise generates a new random identifier.
    """
    if header_value is None:
        return uuid.uuid4().hex

    value = header_value.strip()
    if not value or len(value) > _REQUEST_UUID_MAX_LENGTH:
        return uuid.uuid4().hex

    if not _REQUEST_UUID_RE.match(value):
        return uuid.uuid4().hex

    return value


# NOTE (ADR-19): Request context is reset before and after request.
# This guarantees isolation between concurrent requests and prevents
# leakage of context data across execution boundaries.

async def request_context_middleware(request: Request, call_next):
    """
    Populate request-scoped context for the duration of the request.
    Initializes context variables (request_uuid, request_start_time)
    and ensures cleanup after request processing.
    """
    reset_context()

    try:
        header_value = request.headers.get("X-Request-ID")
        request_uuid = resolve_request_uuid(header_value)
        set_context_var("request_uuid", request_uuid)
        set_context_var("request_start_time", time.perf_counter())

        response = await call_next(request)

        response.headers["X-Request-ID"] = request_uuid
        return response

    finally:
        reset_context()
