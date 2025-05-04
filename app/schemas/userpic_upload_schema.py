"""
The module defines Pydantic schemas for uploading a user's profile
picture.
"""

from pydantic import BaseModel


class UserpicUploadResponse(BaseModel):
    """
    Response schema for the successful upload of a user's profile
    picture. Contains the user's unique identifier associated with
    the newly uploaded profile picture.
    """
    user_id: int
