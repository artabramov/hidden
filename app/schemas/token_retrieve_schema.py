"""
The module defines Pydantic schemas for retrieving a user token.
"""

from typing import Optional
from pydantic import BaseModel, Field, field_validator
from app.validators.username_validator import username_validate
from app.validators.user_totp_validator import user_totp_validate


class TokenRetrieveRequest(BaseModel):
    """
    Request schema for retrieving a user token. Contains the username,
    the time-based one-time password for multi-factor authentication,
    and an optional token expiration time. The totp must be a 6-digit
    numeric value. If provided, it indicates the desired expiration
    time of the token.
    """
    username: str = Field(..., min_length=2, max_length=47)
    user_totp: str = Field(..., min_length=6, max_length=6)
    token_exp: Optional[int] = Field(default=None, ge=1)

    class Config:
        """Strips whitespaces at the beginning and end of all values."""
        str_strip_whitespace = True

    @field_validator("username", mode="before")
    def validate_username(cls, username: str) -> str:
        """Validates username."""
        return username_validate(username)

    @field_validator("user_totp", mode="before")
    def filter_user_totp(cls, user_totp: str) -> str:
        """Validates user totp."""
        return user_totp_validate(user_totp)


class TokenRetrieveResponse(BaseModel):
    """
    Response schema for retrieving a user token. Contains the generated
    user token that is returned after a successful authentication and
    token generation process.
    """
    user_token: str
