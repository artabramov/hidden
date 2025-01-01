"""
The module defines Pydantic schema for retrieving a heartbeat data.
"""

from pydantic import BaseModel


class HeartbeatRetrieveResponse(BaseModel):
    """
    Pydantic schema for the response when retrieving a heartbeat data.
    """
    unix_timestamp: int
    timezone_name: str
    timezone_offset: int
    is_locked: bool
    locked_date: int
