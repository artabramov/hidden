"""Initializes a global app logger."""

import logging
from concurrent_log_handler import ConcurrentRotatingFileHandler
from fastapi import FastAPI


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
