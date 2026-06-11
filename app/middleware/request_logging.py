# app/middleware/request_logging.py
# SPDX-License-Identifier: GPL-3.0-only

import logging
import time

from fastapi import Request

from app.context import get_context_var
from app.events import Events as E

logger = logging.getLogger(__name__)


async def request_logging_middleware(request: Request, call_next):
    """
    Log request lifecycle events with basic metadata. Emits logs for
    request start, completion and failure, including elapsed time.
    """
    client = request.client.host if request.client else None
    logger.info(
        "event=%s method=%s url=%s client=%s",
        E.REQUEST_STARTED,
        request.method,
        request.url,
        client,
    )

    try:
        response = await call_next(request)

        start_time = get_context_var("request_start_time")
        elapsed_time = time.perf_counter() - start_time
        logger.info(
            "event=%s status_code=%s elapsed_time=%.6f",
            E.REQUEST_COMPLETED,
            response.status_code,
            elapsed_time,
        )

    except Exception:
        logger.exception("event=%s", E.REQUEST_FAILED)
        raise

    return response
