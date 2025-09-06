"""Pydantic schemas for user registration."""

from typing import Optional
from pydantic import (
    BaseModel, Field, field_validator, SecretStr, ConfigDict)
from app.validators.user_validators import (
    username_validate, summary_validate, password_validate)


class UserRegisterRequest(BaseModel):
    """
    Request schema for user registration request with validation
    of username, password, names, and optional profile summary.
    """
    model_config = ConfigDict(str_strip_whitespace=True)

    username: str = Field(..., min_length=2, max_length=40)
    password: SecretStr = Field(..., min_length=6)
    first_name: str = Field(..., min_length=1, max_length=40)
    last_name: str = Field(..., min_length=1, max_length=40)
    summary: Optional[str] = Field(default=None, max_length=4096)

    @field_validator("username", mode="before")
    @classmethod
    def _validate_username(cls, value: str) -> str:
        """Validates username: strips, lowercases and [a-z0-9_] only."""
        return username_validate(value)

    @field_validator("password", mode="before")
    @classmethod
    def _validate_password(cls, value: str) -> str:
        """
        Validates password complexity: must include upper, lower, digit,
        and special char, no spaces.
        """
        return password_validate(value)

    @field_validator("summary", mode="before")
    @classmethod
    def _validate_summary(cls, value: Optional[str]) -> Optional[str]:
        """
        Validates summary: trims whitespace and converts blank strings
        to None.
        """
        return summary_validate(value)


class UserRegisterResponse(BaseModel):
    """
    Response schema for user registration response including assigned
    user ID and MFA secret string.
    """
    user_id: int
    mfa_secret: str
