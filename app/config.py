# app/config.py
# SPDX-License-Identifier: Apache-2.0

import os
from functools import cached_property, lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict

from app.constants import (
    GOCRYPTFS_PASSPHRASE_FILENAME,
    VERSITY_ACCESS_KEY_FILENAME,
    VERSITY_SECRET_KEY_FILENAME,
    VERSITY_DATA_DIRNAME,
    VERSITY_IAM_DIRNAME,
)


class Config(BaseSettings):
    """
    Combine environment-based settings and derived filesystem
    paths into the application runtime configuration.
    """

    INSTALL_SOURCE_CODE: str
    INSTALL_CIPHERDIR: str
    INSTALL_MOUNTPOINT: str
    INSTALL_SECRETS: str
    UVICORN_HOST: str
    UVICORN_PORT: int
    WATCHDOG_INTERVAL_SECONDS: int
    WATCHDOG_LIVENESS_SECONDS: int
    API_PREFIX: str
    LOG_LEVEL: str
    LOG_FORMAT: str
    CORS_ALLOW_ORIGINS: str
    CORS_MAX_AGE_SECONDS: int
    VERSITY_HOST: str
    VERSITY_PORT: int
    VERSITY_WEBGUI_HOST: str
    VERSITY_WEBGUI_PORT: int
    VERSITY_WEBGUI_GATEWAY: str
    VERSITY_WEBGUI_CORS_ALLOW_ORIGIN: str
    VERSITY_START_TIMEOUT_SECONDS: float
    VERSITY_STOP_TIMEOUT_SECONDS: int
    VERSITY_POLL_INTERVAL_SECONDS: float

    @cached_property
    def GOCRYPTFS_PASSPHRASE_PATH(self) -> str:
        return os.path.join(
            self.INSTALL_SECRETS,
            GOCRYPTFS_PASSPHRASE_FILENAME,
        )

    @cached_property
    def VERSITY_ACCESS_KEY_PATH(self) -> str:
        return os.path.join(
            self.INSTALL_SECRETS,
            VERSITY_ACCESS_KEY_FILENAME,
        )

    @cached_property
    def VERSITY_SECRET_KEY_PATH(self) -> str:
        return os.path.join(
            self.INSTALL_SECRETS,
            VERSITY_SECRET_KEY_FILENAME,
        )

    @cached_property
    def VERSITY_DATA_PATH(self) -> str:
        return os.path.join(
            self.INSTALL_MOUNTPOINT,
            VERSITY_DATA_DIRNAME,
        )

    @cached_property
    def VERSITY_IAM_PATH(self) -> str:
        return os.path.join(
            self.INSTALL_MOUNTPOINT,
            VERSITY_IAM_DIRNAME,
        )

    model_config = SettingsConfigDict(
        extra="ignore",
    )


@lru_cache(maxsize=1)
def get_config() -> Config:
    """
    Create and return a cached application configuration instance
    populated from the environment.
    """
    return Config()
