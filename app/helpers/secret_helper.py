"""
The module contains asynchronous functions for working with the app's
secret key, including checking for its existence and reading its value.
"""

from app.managers.file_manager import FileManager
from app.config import get_config

cfg = get_config()


async def secret_exists() -> bool:
    """
    Checks whether the app's secret key file exists at the configured
    path.
    """
    return await FileManager.file_exists(cfg.SECRET_KEY_PATH)


async def secret_read() -> str:
    """
    Reads the secret key from the configured file path and returns it
    as a decoded string.
    """
    secret_bin = await FileManager.read(cfg.SECRET_KEY_PATH)
    return secret_bin.decode()
