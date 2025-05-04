"""
The module defines Pydantic schemas for creating a lock.
"""

from pydantic import BaseModel


class LockCreateResponse(BaseModel):
    """
    Response schema for the creation of a lock. Contains a boolean flag
    indicating whether the lock was successfully created or if it
    already exists.
    """
    lock_exists: bool
