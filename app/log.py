"""
The module sets up logging for the application with context-aware
capabilities. It configures a rotating file handler to manage log files,
ensures proper log rotation based on size, and maintains a specified
number of backup files. The logging system is enhanced with a custom
filter that adds context-specific information, such as trace request
UUIDs, to each log message. This setup helps in tracking and correlating
log entries within the same context effectively.
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
    A logging filter that adds context-specific information to log
    records. The filter appends a trace request UUID to each log
    message, enabling better tracking and correlation of log entries
    within the same context.
    """
    def filter(self, message: object) -> bool:
        message.trace_request_uuid = ctx.trace_request_uuid
        return True


@lru_cache
def get_log():
    """
    Creates and configures a rotating file logger with context-specific
    filtering. The logger writes logs to a file with rotation based on
    size and keeps a limited number of backup files. It applies a custom
    filter to include trace request UUIDs in log messages.
    """
    handler = RotatingFileHandler(
        filename=cfg.LOG_FILENAME, maxBytes=cfg.LOG_FILESIZE,
        backupCount=cfg.LOG_FILES_LIMIT)
    handler.setFormatter(logging.Formatter(cfg.LOG_FORMAT))

    log = logging.getLogger(cfg.LOG_NAME)
    log.addHandler(handler)
    log.addFilter(ContextualFilter())
    log.setLevel(logging.getLevelName(cfg.LOG_LEVEL))
    return log
