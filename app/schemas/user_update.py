"""Pydantic schemas for user update."""

from typing import Optional
from pydantic import BaseModel, Field, field_validator, ConfigDict
from app.validators.user_validators import summary_validate


class UserUpdateRequest(BaseModel):
    """
    Request schema for updating a user profile. Requires first and last
    name; summary is optional. Whitespace is stripped from strings;
    extra fields are forbidden.
    """

    model_config = ConfigDict(
        str_strip_whitespace=True,
        extra="forbid",
    )

    first_name: str = Field(..., min_length=1, max_length=40)
    last_name: str = Field(..., min_length=1, max_length=40)
    summary: Optional[str] = Field(default=None, max_length=4096)

    @field_validator("summary")
    @classmethod
    def _validate_summary(cls, value: Optional[str]) -> Optional[str]:
        return summary_validate(value)


class UserUpdateResponse(BaseModel):
    """
    Response schema for user update. Contains the updated user ID.
    """

    user_id: int
