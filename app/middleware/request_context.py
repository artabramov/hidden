# app/middleware/request_context.py
# SPDX-License-Identifier: Apache-2.0

import re
import time
import uuid

from fastapi import Request

from app.context import reset_context, set_context_var

_REQUEST_UUID_MAX_LENGTH = 64
_REQUEST_UUID_RE = re.compile(
    rf"^[A-Za-z0-9_-]{{1,{_REQUEST_UUID_MAX_LENGTH}}}$",
)


def resolve_request_uuid(header_value: str | None) -> str:
    """
    Return the provided request identifier when it is valid, otherwise
    generate a new random identifier.
    """
    if header_value is None:
        return uuid.uuid4().hex

    value = header_value.strip()
    if not value or len(value) > _REQUEST_UUID_MAX_LENGTH:
        return uuid.uuid4().hex

    if not _REQUEST_UUID_RE.match(value):
        return uuid.uuid4().hex

    return value


async def request_context_middleware(request: Request, call_next):
    """
    Initialize request-scoped context with a request identifier and
    start time, add the identifier to the response headers, and reset
    the context after request processing.
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
