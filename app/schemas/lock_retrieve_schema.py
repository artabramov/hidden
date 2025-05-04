"""
The module defines Pydantic schemas for lock retrieval.
"""

from pydantic import BaseModel


class LockRetrieveResponse(BaseModel):
    """
    Response schema for retrieving the status of a lock. Contains a
    boolean flag indicating whether the lock exists or not.
    """
    lock_exists: bool
