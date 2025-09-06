"""Pydantic schemas for user deletion."""

from pydantic import BaseModel


class UserDeleteResponse(BaseModel):
    """
    Response schema for confirming a user deletion by returning the
    unique identifier of the removed account.
    """
    user_id: int
