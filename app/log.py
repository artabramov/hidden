"""
Configures the application logger with a rotating file handler and a
contextual filter that injects the request UUID into log records for
better traceability.
"""

import logging
from functools import lru_cache
from logging import Filter
from logging.handlers import RotatingFileHandler
from app.config import get_config
from app.context import get_context

cfg = get_config()
ctx = get_context()


class ContextualFilter(Filter):
    """
    Logging filter that injects the current request UUID from the app
    context into each log record to improve correlation and traceability
    across related log entries.
    """

    def filter(self, message: object):
        """
        Attaches the request UUID from the context to the provided log
        record and returns True to allow the message to be processed by
        subsequent handlers and formatters.
        """
        message.request_uuid = ctx.request_uuid
        return True


@lru_cache
def get_log():
    """
    Creates or returns a cached logger configured with a rotating file
    handler, custom formatting, a contextual filter for request UUIDs,
    and a log level derived from application settings.
    """
    handler = RotatingFileHandler(
        filename=cfg.LOG_FILENAME,
        maxBytes=cfg.LOG_FILESIZE,
        backupCount=cfg.LOG_FILES_LIMIT
    )
    handler.setFormatter(logging.Formatter(cfg.LOG_FORMAT))

    log = logging.getLogger(cfg.LOG_NAME)
    log.addHandler(handler)
    log.addFilter(ContextualFilter())
    log.setLevel(cfg.LOG_LEVEL)
    return log
