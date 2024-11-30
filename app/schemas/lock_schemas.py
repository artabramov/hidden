"""
The module defines Pydantic schemas for managing the lockdown state of
the application. Includes schemas for retrieving and updating the
lockdown status.
"""

from pydantic import BaseModel


class LockRetrieveResponse(BaseModel):
    """
    Pydantic schema for the response when retrieving the application's
    lockdown status. Includes a flag indicating whether the application
    is locked and the date of lockdown.
    """
    is_locked: bool
    locked_date: int


class LockUpdateRequest(BaseModel):
    """
    Pydantic schema for a request to update the application's lockdown
    status. Includes a flag to specify whether the application should be
    locked or unlocked.
    """
    is_locked: bool


class LockUpdateResponse(BaseModel):
    """
    Pydantic schema for the response after updating the application's
    lockdown status. Includes the updated lockdown status flag.
    """
    is_locked: bool
