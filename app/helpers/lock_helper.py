"""
The module provides functionality for managing a lock file to control
access to the application. It includes functions for checking the lock
status, retrieving the locked date, enabling and disabling the lock, and
preventing concurrent access or indicating a restricted state.
"""

import os
from app.managers.file_manager import FileManager
from app.config import get_config

cfg = get_config()


def is_locked():
    """
    Checks if the lock file exists at the configured path and returns
    True if it does, indicating that the system is in a locked state;
    otherwise, returns False.
    """
    return os.path.isfile(cfg.APP_LOCK_PATH)


def locked_date():
    """Retrieve locked date."""
    return (int(os.path.getctime(cfg.APP_LOCK_PATH))
            if is_locked() else 0)


async def lock_enable():
    """
    Creates a lock file if the system is not already locked. The lock
    file is used to prevent concurrent access or indicate a restricted
    state. The function only writes the lock file if it does not
    already exist.
    """
    if not is_locked():
        await FileManager.write(cfg.APP_LOCK_PATH, bytes())


async def lock_disable():
    """
    Removes the lock file if it exists, thereby unlocking the system.
    The function only deletes the lock file if the system is currently
    locked. This is typically used to signal the end of a restricted
    state or maintenance period.
    """
    if is_locked():
        await FileManager.delete(cfg.APP_LOCK_PATH)
