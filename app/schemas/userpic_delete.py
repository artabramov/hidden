"""Pydantic schemas for userpic deletion."""

from pydantic import BaseModel


class UserpicDeleteResponse(BaseModel):
    """
    Response schema for userpic deletion. Contains the user ID.
    """

    user_id: int
