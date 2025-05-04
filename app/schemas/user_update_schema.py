"""
The module defines Pydantic schemas for user registration and updating
user information.
"""

from typing import Optional
from pydantic import BaseModel, Field, field_validator
from app.validators.user_summary_validator import user_summary_validate


class UserUpdateRequest(BaseModel):
    """
    Request schema for updating a user's datan. Allows the update of
    a user's first name, last name, and optional user summary. All
    fields are stripped of leading and trailing whitespace before
    being saved.
    """

    first_name: str = Field(..., min_length=1, max_length=47)
    last_name: str = Field(..., min_length=1, max_length=47)
    user_summary: Optional[str] = Field(max_length=4095, default=None)

    class Config:
        """Strips whitespaces at the beginning and end of all values."""
        str_strip_whitespace = True

    @field_validator("user_summary", mode="before")
    def validate_user_summary(
            cls, user_summary: Optional[str]) -> Optional[str]:
        """Validates user summary."""
        return user_summary_validate(user_summary)


class UserUpdateResponse(BaseModel):
    """
    Response schema for the successful update of a user's personal
    information. Contains the user's unique identifier that reflects
    the updated user record.
    """
    user_id: int
