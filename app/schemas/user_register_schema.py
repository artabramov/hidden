"""
The module defines Pydantic schemas for user registration.
"""

from typing import Optional
from pydantic import BaseModel, Field, field_validator
from app.validators.username_validator import username_validate
from app.validators.user_password_validator import user_password_validate
from app.validators.user_summary_validator import user_summary_validate


class UserRegisterRequest(BaseModel):
    """
    Request schema for registering a new user. Contains required fields
    for user registration including username, password, first name, last
    name, and an optional user summary. The username must consist of
    only latin letters and numbers. The password must contain at least
    one lowercase letter, one uppercase letter, one digit, one special
    character, and no spaces.
    """
    username: str = Field(..., min_length=2, max_length=47)
    password: str = Field(..., min_length=6)
    first_name: str = Field(..., min_length=1, max_length=47)
    last_name: str = Field(..., min_length=1, max_length=47)
    user_summary: Optional[str] = Field(max_length=4095, default=None)

    class Config:
        """Strips whitespaces at the beginning and end of all values."""
        str_strip_whitespace = True

    @field_validator("username", mode="before")
    def validate_username(cls, username: str) -> str:
        """Validates username."""
        return username_validate(username)

    @field_validator("password", mode="before")
    def validate_password(cls, password: str) -> str:
        """Validates user password."""
        return user_password_validate(password)

    @field_validator("user_summary", mode="before")
    def validate_user_summary(
            cls, user_summary: Optional[str]) -> Optional[str]:
        """Validates user summary."""
        return user_summary_validate(user_summary)


class UserRegisterResponse(BaseModel):
    """
    Pydantic schema for the response after registering a new user.
    Includes the user ID and secret for MFA.
    """
    user_id: int
    mfa_secret: str
