"""
The module provides asynchronous functions for managing the app lock
file, including checking its existence, creating it, and deleting it.
"""

from app.managers.file_manager import FileManager
from app.config import get_config

cfg = get_config()


async def lock_exists():
    """Checks whether the app lock file exists at the configured path."""
    return await FileManager.file_exists(cfg.APP_LOCK_PATH)


async def lock_enable():
    """Creates the application lock file if it does not already exist."""
    if not await lock_exists():
        await FileManager.write(cfg.APP_LOCK_PATH, bytes())


async def lock_disable():
    """Deletes the app lock file if it exists."""
    if await lock_exists():
        await FileManager.delete(cfg.APP_LOCK_PATH)
