# app/middleware/cors_setup.py
# SPDX-License-Identifier: GPL-3.0-only

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_config


def cors_setup_middleware(app: FastAPI) -> None:
    """
    Configure Cross-Origin Resource Sharing (CORS).

    Browsers enforce same-origin restrictions for cross-origin requests.
    Configured origins receive CORS response headers allowing access to
    the API across different origins.
    """
    config = get_config()

    app.add_middleware(
        CORSMiddleware,
        allow_origins=config.CORS_ALLOW_ORIGINS_LIST,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        max_age=config.CORS_MAX_AGE_SECONDS,
    )
