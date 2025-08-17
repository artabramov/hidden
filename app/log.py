"""
The module configures and provides a logger instance for the app.
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
    A custom logging filter that adds contextual information to log
    messages. This filter attaches a request UUID from the app context
    to each log message, enabling better tracking and correlation of
    log entries related to a specific request.
    """

    def filter(self, message: object):
        """
        Filters the log message by adding the request UUID from the
        context.
        """
        message.request_uuid = ctx.request_uuid
        return True


@lru_cache
def get_log():
    """
    Returns a configured logger instance. The logger is configured with
    a rotating file handler to handle log file rotation. The logger's
    log level is set according to the configuration.
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
