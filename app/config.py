"""
Defines the configuration settings for the application using a dataclass
to hold various configuration parameters. Loads these settings from an
.env file using dotenv and converts them to the appropriate types.
Utilizes an LRU cache to store the configuration object for efficient
retrieval.
"""

from dotenv import dotenv_values
from dataclasses import dataclass, fields
from functools import lru_cache

DOTENV_FILE = "/hidden/.env"


def read_secret_key(filepath: str) -> str:
    with open(filepath, "r") as fn:
        return fn.read().strip()


@dataclass
class Config:
    CRYPTOGRAPHY_PASSWORD: None
    CRYPTOGRAPHY_PASSWORD_PATH: str
    CRYPTOGRAPHY_SALT_LENGTH: int
    CRYPTOGRAPHY_KEY_LENGTH: int
    CRYPTOGRAPHY_IV_LENGTH: int
    CRYPTOGRAPHY_PBKDF2_ITERATIONS: int

    HASHLIB_SALT: str

    UVICORN_HOST: str
    UVICORN_PORT: int
    UVICORN_WORKERS: int

    POSTGRES_HOST: str
    POSTGRES_PORT: int
    POSTGRES_DATABASE: str
    POSTGRES_USERNAME: str
    POSTGRES_PASSWORD: str
    POSTGRES_POOL_SIZE: int
    POSTGRES_POOL_OVERFLOW: int

    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_DECODE: bool
    REDIS_EXPIRE: int

    LOG_LEVEL: str
    LOG_NAME: str
    LOG_FORMAT: str
    LOG_FILENAME: str
    LOG_FILESIZE: int
    LOG_FILES_LIMIT: int

    MFA_APP_NAME: str
    MFA_MIMETYPE: str
    MFA_VERSION: int
    MFA_BOX_SIZE: int
    MFA_BORDER: int
    MFA_FIT: bool
    MFA_COLOR: str
    MFA_BACKGROUND: str

    JWT_SECRET: str
    JWT_EXPIRES: int
    JWT_ALGORITHM: str
    JTI_LENGTH: int

    USER_LOGIN_ATTEMPTS: int
    USER_MFA_ATTEMPTS: int
    USER_SUSPENDED_TIME: int

    USERPIC_BASE_PATH: str
    USERPIC_BASE_URL: str
    USERPIC_PREFIX: str
    USERPIC_MIMES: list
    USERPIC_EXTENSION: str
    USERPIC_MODE: str
    USERPIC_WIDTH: int
    USERPIC_HEIGHT: int
    USERPIC_QUALITY: int

    SHRED_OVERWRITE_CYCLES: int

    SHARD_BASE_PATH: str
    SHARD_SIZE: int

    SHUFFLE_ENABLED: bool
    SHUFFLE_LOCKED: bool
    SHUFFLE_LIMIT: int
    SHUFFLE_EXTENSION: str

    THUMBNAILS_BASE_URL: str
    THUMBNAILS_BASE_PATH: str
    THUMBNAILS_EXTENSION: str
    THUMBNAILS_PREFIX: str
    THUMBNAIL_WIDTH: int
    THUMBNAIL_HEIGHT: int
    THUMBNAIL_QUALITY: int

    PARTNERPIC_BASE_PATH: str
    PARTNERPIC_BASE_URL: str
    PARTNERPIC_PREFIX: str
    PARTNERPIC_MIMES: str
    PARTNERPIC_EXTENSION: str
    PARTNERPIC_MODE: str
    PARTNERPIC_WIDTH: int
    PARTNERPIC_HEIGHT: int
    PARTNERPIC_QUALITY: int

    APP_OPENAPI_TAGS_PATH: str
    APP_LOCK_PATH: str
    APP_SCHEDULER_RATE: int
    APP_HTML_PATH: str
    APP_BASE_URL: str
    APP_PREFIX: str
    APP_TITLE: str

    PLUGINS_BASE_PATH: str
    PLUGINS_ENABLED: list

    TEMP_PATH: str


@lru_cache(maxsize=None)
def get_config() -> Config:
    """
    Loads configuration settings from an .env file and returns them as a
    Config dataclass instance. The function uses type hints to convert
    the environment variable values to their appropriate types, such as
    int, list, or bool. Caches the result to optimize performance
    for subsequent calls.
    """
    keys_and_types = {x.name: x.type for x in fields(Config)}
    values = dotenv_values(DOTENV_FILE)
    config_dict = {}

    for key, value in values.items():
        value_type = keys_and_types.get(key)

        if value_type is None:
            value = None

        elif value_type == int:
            value = int(value)

        elif value_type == list:
            value = value.split(",")

        elif value_type == bool:
            value = value.lower() == "true"

        config_dict[key] = value

    config_dict["CRYPTOGRAPHY_PASSWORD"] = read_secret_key(
        config_dict["CRYPTOGRAPHY_PASSWORD_PATH"])

    return Config(**config_dict)
