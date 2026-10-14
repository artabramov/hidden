# app/middleware/cors_setup.py
# SPDX-License-Identifier: Apache-2.0

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_config


def cors_setup_middleware(app: FastAPI) -> None:
    """
    Configure CORS middleware with the allowed origins and preflight
    cache duration defined in the application configuration.
    """
    config = get_config()
    allow_origins = [
        origin.strip()
        for origin in config.CORS_ALLOW_ORIGINS.split(",")
        if origin.strip()
    ]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=allow_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        max_age=config.CORS_MAX_AGE_SECONDS,
    )
