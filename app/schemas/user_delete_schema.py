"""
The module defines Pydantic schemas for handling user deletion.
"""

from pydantic import BaseModel


class UserDeleteResponse(BaseModel):
    """
    Response schema for the successful deletion of a user. Contains the
    user's unique identifier that confirms the deletion was applied to
    the specific user record.
    """
    user_id: int
