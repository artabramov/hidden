"""
The module defines Pydantic schemas for managing the lock status of
the application. Includes schemas for updating the lock status.
"""

from pydantic import BaseModel


class LockUpdateRequest(BaseModel):
    """
    Pydantic schema for a request to update the application's lock
    status. Includes a flag to specify whether the application should be
    locked or unlocked.
    """
    is_locked: bool


class LockUpdateResponse(BaseModel):
    """
    Pydantic schema for the response after updating the application's
    lock status. Includes the updated lockdown status flag.
    """
    is_locked: bool
