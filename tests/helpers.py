# tests/helpers.py
# SPDX-License-Identifier: SSPL-1.0

import os


def build_default_config_values() -> dict[str, object]:
    return {
        "INSTALL_SOURCE_DIR": "/opt/hidden",
        "INSTALL_STATE_DIR": "/state",
        "INSTALL_SECRETS_DIR": "/secrets",
        "INSTALL_EXTENSIONS_DIR": "/extensions",
        "LOG_LEVEL": "INFO",
        "LOG_FORMAT": "%(message)s",
        "GOCRYPTFS_WATCHDOG_INTERVAL_SECONDS": 60,
        "GOCRYPTFS_WATCHDOG_LIVENESS_SECONDS": 120,
        "SQLITE_JOURNAL_MODE": "WAL",
        "SQLITE_SYNCHRONOUS": "NORMAL",
        "SQLITE_BUSY_TIMEOUT": 10000,
        "SQLITE_TEMP_STORE": "MEMORY",
        "UVICORN_HOST": "127.0.0.1",
        "UVICORN_PORT": 80,
        "API_PREFIX": "/api/v1",
        "AUTH_TOKEN_TTL_SECONDS": 86400,
        "CORS_ALLOW_ORIGINS": "http://localhost:3000,http://127.0.0.1:3000",
        "CORS_MAX_AGE_SECONDS": 86400,
        "ENABLED_EXTENSIONS": "",
    }


def set_minimal_app_config_env() -> None:
    env_values = {
        key: str(value)
        for key, value in build_default_config_values().items()
    }
    for key, value in env_values.items():
        os.environ.setdefault(key, value)
