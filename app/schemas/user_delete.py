"""Pydantic schemas for user deletion."""

from pydantic import BaseModel


class UserDeleteResponse(BaseModel):
    """
    Response schema for user deletion. Contains the deleted user ID.
    """

    user_id: int
