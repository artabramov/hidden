"""Pydantic schemas for uploading a user's image."""

from pydantic import BaseModel


class UserpicUploadResponse(BaseModel):
    """
    Response schema confirming a successful user image upload by
    returning the unique identifier of the affected user account.
    """
    user_id: int
