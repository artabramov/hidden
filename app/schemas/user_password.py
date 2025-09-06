"""Pydantic schemas for changing a user's password."""

from pydantic import BaseModel, Field, field_validator, ConfigDict
from app.validators.user_validators import password_validate


class UserPasswordRequest(BaseModel):
    """
    Request schema for changing a user's password, including the current
    password and the new password, where the new one is trimmed and
    validated for required complexity.
    """
    model_config = ConfigDict(str_strip_whitespace=True)

    current_password: str = Field(..., min_length=6)
    updated_password: str = Field(..., min_length=6)

    @field_validator("updated_password", mode="before")
    @classmethod
    def _validate_updated_password(cls, v: str) -> str:
        return password_validate(v)


class UserPasswordResponse(BaseModel):
    """
    Response schema confirming a password change by returning the unique
    identifier of the affected user account.
    """
    user_id: int
