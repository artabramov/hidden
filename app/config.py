# app/config.py
# SPDX-License-Identifier: SSPL-1.0

import os
from functools import cached_property, lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict

from app.constants import (
    FERNET_KEY_FILENAME,
    FILES_DIRNAME,
    FILES_REVISIONS_DIRNAME,
    FILES_THUMBNAILS_DIRNAME,
    FILES_TMP_DIRNAME,
    FIRST_ADMIN_CREATED_FLAG_FILENAME,
    GOCRYPTFS_CIPHER_DIRNAME,
    GOCRYPTFS_MOUNTPOINT_DIRNAME,
    GOCRYPTFS_PASSPHRASE_ENCRYPTED_FILENAME,
    JWT_SIGNING_KEY_FILENAME,
    SQLITE_DIRNAME,
    SQLITE_FILENAME,
)


class Config(BaseSettings):
    """
    Runtime configuration loaded from environment variables,
    plus computed filesystem paths derived from those values.
    """
    INSTALL_SOURCE_DIR: str
    INSTALL_STATE_DIR: str
    INSTALL_SECRETS_DIR: str
    INSTALL_EXTENSIONS_DIR: str
    LOG_LEVEL: str
    LOG_FORMAT: str
    GOCRYPTFS_WATCHDOG_INTERVAL_SECONDS: int
    GOCRYPTFS_WATCHDOG_LIVENESS_SECONDS: int
    SQLITE_JOURNAL_MODE: str
    SQLITE_SYNCHRONOUS: str
    SQLITE_BUSY_TIMEOUT: int
    SQLITE_TEMP_STORE: str
    UVICORN_HOST: str
    UVICORN_PORT: int
    API_PREFIX: str
    AUTH_TOKEN_TTL_SECONDS: int
    AUTH_ALLOW_PERMANENT_TOKENS: bool = False
    LRU_CACHE_MAX_BYTES: int = 0
    CORS_ALLOW_ORIGINS: str = ""
    CORS_MAX_AGE_SECONDS: int = 0
    ENABLED_EXTENSIONS: str = ""

    @cached_property
    def GOCRYPTFS_PASSPHRASE_ENCRYPTED_PATH(self) -> str:
        return os.path.join(
            self.INSTALL_SECRETS_DIR,
            GOCRYPTFS_PASSPHRASE_ENCRYPTED_FILENAME,
        )

    @cached_property
    def FIRST_ADMIN_CREATED_FLAG_PATH(self) -> str:
        return os.path.join(
            self.INSTALL_SECRETS_DIR,
            FIRST_ADMIN_CREATED_FLAG_FILENAME,
        )

    @cached_property
    def GOCRYPTFS_CIPHERDIR(self) -> str:
        return os.path.join(
            self.INSTALL_STATE_DIR,
            GOCRYPTFS_CIPHER_DIRNAME,
        )

    @cached_property
    def GOCRYPTFS_MOUNTPOINT(self) -> str:
        return os.path.join(
            self.INSTALL_STATE_DIR,
            GOCRYPTFS_MOUNTPOINT_DIRNAME,
        )

    @cached_property
    def SQLITE_DIR(self) -> str:
        return os.path.join(
            self.GOCRYPTFS_MOUNTPOINT,
            SQLITE_DIRNAME,
        )

    @cached_property
    def SQLITE_PATH(self) -> str:
        return os.path.join(
            self.SQLITE_DIR,
            SQLITE_FILENAME,
        )

    @cached_property
    def SQLITE_URL(self) -> str:
        return "sqlite+aiosqlite:///" + self.SQLITE_PATH

    @cached_property
    def FILES_DIR(self) -> str:
        return os.path.join(
            self.GOCRYPTFS_MOUNTPOINT,
            FILES_DIRNAME,
        )

    @cached_property
    def FILES_REVISIONS_DIR(self) -> str:
        return os.path.join(
            self.GOCRYPTFS_MOUNTPOINT,
            FILES_REVISIONS_DIRNAME,
        )

    @cached_property
    def FILES_THUMBNAILS_DIR(self) -> str:
        return os.path.join(
            self.GOCRYPTFS_MOUNTPOINT,
            FILES_THUMBNAILS_DIRNAME,
        )

    @cached_property
    def FILES_TMP_DIR(self) -> str:
        return os.path.join(
            self.GOCRYPTFS_MOUNTPOINT,
            FILES_TMP_DIRNAME,
        )

    @cached_property
    def JWT_SIGNING_KEY_PATH(self) -> str:
        return os.path.join(
            self.INSTALL_SECRETS_DIR,
            JWT_SIGNING_KEY_FILENAME,
        )

    @cached_property
    def JWT_SIGNING_KEY(self) -> str:
        with open(self.JWT_SIGNING_KEY_PATH, "r", encoding="utf-8") as f:
            return f.read().strip()

    @cached_property
    def FERNET_KEY_PATH(self) -> str:
        return os.path.join(
            self.INSTALL_SECRETS_DIR,
            FERNET_KEY_FILENAME,
        )

    @cached_property
    def FERNET_KEY(self) -> str:
        """
        Return the Fernet key loaded from the configured file path.
        The value is loaded lazily and cached after the first access.
        """
        with open(self.FERNET_KEY_PATH, "r", encoding="utf-8") as f:
            return f.read().strip()

    @cached_property
    def CORS_ALLOW_ORIGINS_LIST(self) -> list[str]:
        return self._csv_to_list(self.CORS_ALLOW_ORIGINS)

    @cached_property
    def ENABLED_EXTENSIONS_LIST(self) -> list[str]:
        requested = self._csv_to_list(self.ENABLED_EXTENSIONS)
        if not requested:
            return []

        root = self.INSTALL_EXTENSIONS_DIR
        installed = {
            name for name in os.listdir(root)
            if os.path.isdir(os.path.join(root, name))
        }

        missing = set(requested) - installed
        if missing:
            raise ValueError(
                "Missing extensions: " + ", ".join(sorted(missing))
            )

        return requested

    @staticmethod
    def _csv_to_list(value: str) -> list[str]:
        return [item.strip() for item in value.split(",") if item.strip()]

    model_config = SettingsConfigDict(
        extra="ignore",
    )


# NOTE (ADR-17): Configuration is not initialized at module import time.
# Runtime modules may depend on environment setup and filesystem state,
# which may not be ready during import. Bootstrap modules main.py and
# db.py are the only exceptions.

@lru_cache(maxsize=1)
def get_config() -> Config:
    return Config()
