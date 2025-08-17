"""
The module defines Pydantic schemas for handling token invalidation.
"""

from pydantic import BaseModel


class TokenInvalidateResponse(BaseModel):
    """
    Response schema for the successful invalidation of a user token.
    Contains the user's unique identifier that confirms the token was
    invalidated for the specific user.
    """
    user_id: int
