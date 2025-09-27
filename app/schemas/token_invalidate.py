"""Pydantic schemas for token invalidation."""

from pydantic import BaseModel


class TokenInvalidateResponse(BaseModel):
    """
    Response schema for token invalidation. Confirms that the token
    was invalidated for the specified user by returning the user's
    unique identifier.
    """

    user_id: int
