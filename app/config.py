"""
Defines the application configuration as a dataclass and loads values
from an `.env` file using the `python-dotenv` library, converting them
to the appropriate types; uses `lru_cache` to memoize the resulting
configuration object for efficient reuse.
"""

from dataclasses import dataclass, fields
from functools import lru_cache
from dotenv import dotenv_values

DOTENV_PATH = "/hidden/.env"


@dataclass
class Config:
    """
    Strongly typed configuration where field names must match keys
    in the .env file; values are trimmed and converted according to
    their annotated types.
    """
    SECRET_KEY_PATH: str
    SECRET_KEY_LENGTH: int
    SECRET_KEY_WATCHDOG_INTERVAL_SECONDS: int

    DATA_MOUNTPOINT: str
    DATA_CIPHER_DIR: str

    CRYPTO_KEY_LENGTH: int
    CRYPTO_NONCE_LENGTH: int
    CRYPTO_HKDF_INFO: bytes
    CRYPTO_HKDF_SALT_B64: str
    CRYPTO_DERIVE_WITH_HKDF: bool
    CRYPTO_DEFAULT_ENCODING: str
    CRYPTO_AAD_DEFAULT: bytes

    LOCK_FILE_PATH: str

    LOG_LEVEL: str
    LOG_NAME: str
    LOG_FORMAT: str
    LOG_FILENAME: str
    LOG_FILESIZE: int
    LOG_FILES_LIMIT: int

    UVICORN_HOST: str
    UVICORN_PORT: int
    UVICORN_WORKERS: int

    SQLITE_PATH: str
    SQLITE_POOL_SIZE: int
    SQLITE_POOL_OVERFLOW: int
    SQLITE_SQL_ECHO: bool

    REDIS_ENABLED: bool
    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_DECODE_RESPONSES: bool
    REDIS_EXPIRE: int

    LRU_TOTAL_SIZE_BYTES: int
    LRU_ITEM_SIZE_LIMIT_BYTES: int

    FILE_CHUNK_SIZE: int
    FILE_SHRED_CYCLES: int
    FILE_DEFAULT_MIMETYPE: str

    JTI_LENGTH: int
    JWT_ALGORITHMS: list
    JWT_SECRET: str

    ADDONS_PATH: str
    ADDONS_LIST: list

    AUTH_PASSWORD_ATTEMPTS: int
    AUTH_TOTP_ATTEMPTS: int
    AUTH_SUSPENDED_TIME: int

    DOCUMENTS_DIR: str
    REVISIONS_DIR: str
    TEMPORARY_DIR: str

    THUMBNAILS_DIR: str
    THUMBNAILS_WIDTH: int
    THUMBNAILS_HEIGHT: int
    THUMBNAILS_QUALITY: int


@lru_cache
def get_config() -> Config:
    """
    Loads configuration settings from an `.env` file and returns them as
    a `Config` dataclass instance. The function uses type annotations to
    convert the environment variable values to their appropriate types,
    such as `bool`, `int`, `list`, `str` or `bytes`.
    """
    env = dotenv_values(DOTENV_PATH)
    cfg = {}

    for field in fields(Config):
        raw = env[field.name]
        type_ = field.type

        if raw == "None":
            cfg[field.name] = None

        elif type_ is list:
            text = raw.strip()
            parts = [] if text == "" else [p.strip() for p in text.split(",")]
            cfg[field.name] = parts

        elif type_ is str:
            cfg[field.name] = raw.strip()

        elif type_ is int:
            cfg[field.name] = int(raw.strip())

        elif type_ is bool:
            value = raw.strip().lower()
            cfg[field.name] = {"true": True, "false": False}[value]

        elif type_ is bytes:
            cfg[field.name] = raw.strip().encode("utf-8")

    return Config(**cfg)
