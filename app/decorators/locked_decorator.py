"""
The module provides functionality for managing a lock file to control
access to application resources. It includes utilities for checking if
the application is locked, creating or removing a lock file
asynchronously, and a decorator to enforce locking on FastAPI routers.
"""

import functools
from typing import Callable, Any
from fastapi import HTTPException


from app.helpers.lock_helper import is_locked


def locked(func: Callable):
    """
    Decorator that enforces a lock based on the existence of a lock file
    before executing the wrapped FastAPI router. If the lock file is
    detected at the path specified in the configuration, a 423 error is
    raised, indicating that the application resource is currently locked.
    """
    @functools.wraps(func)
    async def wrapped(*args, **kwargs) -> Any:
        if is_locked():
            raise HTTPException(status_code=423)
        return await func(*args, **kwargs)
    return wrapped
