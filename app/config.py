"""
Defines the config for the app. Loads settings from the .env file using
dotenv and converts them to the appropriate types. Utilizes an LRU cache
to avoid redundant file operations.
"""

from dotenv import dotenv_values
from dataclasses import dataclass, fields
from functools import lru_cache

DOTENV_PATH = "/hidden/.env"


@dataclass
class Config:
    SECRET_KEY_PATH: str

    CRYPTOGRAPHY_SALT_LENGTH: int
    CRYPTOGRAPHY_KEY_LENGTH: int
    CRYPTOGRAPHY_IV_LENGTH: int
    CRYPTOGRAPHY_PBKDF2_ITERATIONS: int

    LOG_LEVEL: str
    LOG_NAME: str
    LOG_FORMAT: str
    LOG_FILENAME: str
    LOG_FILESIZE: int
    LOG_FILES_LIMIT: int

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

    REDIS_ENABLED: bool
    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_DECODE_RESPONSES: bool
    REDIS_EXPIRE: int

    SPHINX_PATH: str
    SPHINX_NAME: str
    SPHINX_URL: str

    JTI_LENGTH: int
    JWT_EXPIRES: int
    JWT_ALGORITHM: str
    JWT_SECRET: str

    ADDONS_ENABLED: list
    ADDONS_PATH: str

    APP_API_VERSION: str
    APP_URL: str
    APP_SHRED_CYCLES: int
    APP_SHUFFLE_LIMIT: int
    APP_LOCK_PATH: str

    HTML_PATH: str
    HTML_FILE: str

    USER_PASSWORD_ATTEMPTS: int
    USER_TOTP_ATTEMPTS: int
    USER_SUSPENDED_TIME: int

    USERPICS_PATH: str
    USERPICS_URL: str
    USERPICS_PREFIX: str
    USERPICS_WIDTH: int
    USERPICS_HEIGHT: int
    USERPICS_QUALITY: int
    USERPICS_LRU_SIZE: int

    THUMBNAILS_PATH: str
    THUMBNAILS_URL: str
    THUMBNAILS_PREFIX: str
    THUMBNAILS_WIDTH: int
    THUMBNAILS_HEIGHT: int
    THUMBNAILS_QUALITY: int
    THUMBNAILS_LRU_SIZE: int

    DOCUMENTS_PATH: str
    DOCUMENTS_URL: str
    DOCUMENTS_LRU_SIZE: int


@lru_cache
def get_config() -> Config:
    """
    Loads settings from the .env file and returns them as a dataclass
    instance. It uses type hints to convert the environment variable
    values to their appropriate types, such as int, list, or bool.
    Caches the result to optimize performance for subsequent calls.
    """
    keys_and_types = {x.name: x.type for x in fields(Config)}
    values = dotenv_values(DOTENV_PATH)
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

    return Config(**config_dict)
