"""
The module defines Pydantic schemas for user login.
"""

from pydantic import BaseModel, Field, field_validator
from app.validators.username_validator import username_validate


class UserLoginRequest(BaseModel):
    """
    Request schema for logging in a user. Contains the username and
    password fields. The username is converted to lowercase before being
    processed. The password field has a minimum length of 6 characters
    and.
    """
    username: str = Field(..., min_length=2, max_length=47)
    password: str = Field(..., min_length=6)

    class Config:
        """Strips whitespaces at the beginning and end of all values."""
        str_strip_whitespace = True

    @field_validator("username", mode="before")
    def validate_username(cls, username: str) -> str:
        """Validates username."""
        return username_validate(username)


class UserLoginResponse(BaseModel):
    """
    Response schema for the outcome of a user login attempt. Contains a
    boolean flag indicating whether the provided password was accepted
    for the given credentials.
    """
    password_accepted: bool
