"""Pydantic schemas for password change."""

from pydantic import BaseModel, Field, field_validator, ConfigDict
from app.validators.user_validators import password_validate


class UserPasswordRequest(BaseModel):
    """
    Request schema for changing a user's password. Requires the current
    password and a new password. Whitespace is stripped from strings;
    extra fields are forbidden.
    """

    model_config = ConfigDict(
        str_strip_whitespace=True,
        extra="forbid",
    )

    current_password: str = Field(..., min_length=6)
    updated_password: str = Field(..., min_length=6)

    @field_validator("updated_password")
    @classmethod
    def _validate_updated_password(cls, v: str) -> str:
        return password_validate(v)


class UserPasswordResponse(BaseModel):
    """
    Response schema for password change. Contains the user ID.
    """

    user_id: int
