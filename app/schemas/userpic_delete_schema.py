"""
The module defines Pydantic schemas for deleting a user's profile
picture.
"""

from pydantic import BaseModel


class UserpicDeleteResponse(BaseModel):
    """
    Response schema for the successful deletion of a user's profile
    picture. Contains the user's unique identifier that confirms the
    user record associated with the deleted profile picture. This
    response is returned after a successful deletion operation.
    """
    user_id: int
