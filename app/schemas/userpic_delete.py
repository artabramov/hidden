"""Pydantic schema for user image deletion."""

from pydantic import BaseModel


class UserpicDeleteResponse(BaseModel):
    """
    Response confirming successful deletion of a user's image; returns
    the affected user ID.
    """
    user_id: int
