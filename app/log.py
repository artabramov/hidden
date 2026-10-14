# app/log.py
# SPDX-License-Identifier: Apache-2.0

import logging
import sys

from app.config import get_config
from app.context import get_context_var


class RequestContextFilter(logging.Filter):
    """
    Enrich log records with request-scoped context values
    used by the configured log format.
    """

    def filter(self, record: logging.LogRecord) -> bool:
        """
        Populate the log record with the current request identifier
        and allow the record to be processed.
        """
        record.request_uuid = get_context_var("request_uuid", "-")
        return True


def init_logging() -> None:
    """
    Configure the root logger with the configured log level and format,
    replacing existing handlers with a standard output handler enriched
    with request context.
    """
    config = get_config()

    level = getattr(logging, config.LOG_LEVEL.upper(), logging.INFO)
    formatter = logging.Formatter(fmt=config.LOG_FORMAT)

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    handler.addFilter(RequestContextFilter())

    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    root_logger.handlers.clear()
    root_logger.addHandler(handler)
