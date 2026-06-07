# app/log.py
# SPDX-License-Identifier: SSPL-1.0

import logging
import sys

from app.config import get_config
from app.context import get_context_var

# NOTE (ADR-26): Logging is structured across three levels.
# 1. Request-level (middleware): request start, request completion,
#    and unexpected errors are logged in middleware. Each request is
#    assigned a request UUID and includes method, URL, status code, and
#    elapsed time.
# 2. Authentication (dependency auth): authentication and authorization
#    outcomes are logged in the auth dependency. Logs capture reasons for
#    access denial and, on success, associate request UUID with user ID.
# 3. Domain-level (services): services log expected, domain-level
#    outcomes using canonical events. Logs are minimal and do not
#    duplicate request-level or auth-level context.

# NOTE (ADR-27): Sensitive data is not logged.
# Additional identifiers are included in logs only when diagnostically
# useful. Input data, output data, and any sensitive values are not
# written to logs. Logs contain only minimal technical context required
# for diagnostics.

# NOTE (ADR-28): Service logging contract is canonical.
# Service logs use canonical event values. Inline event strings are not
# used. Event values are concise, stable identifiers of service-level
# outcomes.


class RequestContextFilter(logging.Filter):
    """
    Inject request-scoped context values into log records.
    Adds fields expected by the log format (e.g. request_uuid).
    """

    def filter(self, record: logging.LogRecord) -> bool:
        """
        Populate the log record with values from the current context.
        Always returns True to allow the record to be processed.
        """
        record.request_uuid = get_context_var("request_uuid", "-")
        return True


def init_logging() -> None:
    """
    Initialize root logger with configured level, format and handlers.
    Replaces existing handlers and attaches a stream handler with
    request context enrichment.
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
