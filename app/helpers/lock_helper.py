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
    return os.path.isfile(cfg.LOCK_FILE_PATH)


def get_locked_date():
    locked_date = 0
    if is_locked():
        locked_date = int(os.path.getctime(cfg.LOCK_FILE_PATH))
    return locked_date


async def create_lock():
    """
    Creates a lock file if the system is not already locked. The lock
    file is used to prevent concurrent access or indicate a restricted
    state. The function only writes the lock file if it does not
    already exist.
    """
    if not is_locked():
        await FileManager.write(cfg.LOCK_FILE_PATH, bytes())


async def remove_lock():
    """
    Removes the lock file if it exists, thereby unlocking the system.
    The function only deletes the lock file if the system is currently
    locked. This is typically used to signal the end of a restricted
    state or maintenance period.
    """
    if is_locked():
        await FileManager.delete(cfg.LOCK_FILE_PATH)
