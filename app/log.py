"""
Initializes a global app logger and provides a request-scoped adapter
that logs with the current request UUID, using only FastAPI context.
"""

import time
import logging
from uuid import uuid4
from concurrent_log_handler import ConcurrentRotatingFileHandler
from fastapi import FastAPI, Request


def init_logger(app: FastAPI) -> logging.Logger:
    """
    Creates a logger from config, attaches a rotating handler,
    sets level, stores it in app state, and returns it.
    """
    cfg = app.state.config
    handler = ConcurrentRotatingFileHandler(
        filename=cfg.LOG_FILENAME,
        maxBytes=cfg.LOG_FILESIZE,
        backupCount=cfg.LOG_FILES_LIMIT,
        encoding="utf-8",
    )
    handler.setFormatter(logging.Formatter(cfg.LOG_FORMAT))
    log = logging.getLogger(cfg.LOG_NAME)
    if not any(getattr(h, "baseFilename", None) == cfg.LOG_FILENAME
               for h in log.handlers):
        log.addHandler(handler)

    log.setLevel(cfg.LOG_LEVEL)
    log.propagate = False
    app.state.log = log
    return log


def bind_request_logger(request: Request) -> logging.LoggerAdapter:
    """
    Returns a LoggerAdapter bound to request_uuid; if missing, sets
    request_uuid and request_start_time on request.state.
    """
    if not getattr(request.state, "request_uuid", None):
        request.state.request_uuid = str(uuid4())

    if not hasattr(request.state, "request_start_time"):
        request.state.request_start_time = time.time()

    base = request.app.state.log
    return logging.LoggerAdapter(base, {
        "request_uuid": request.state.request_uuid})
