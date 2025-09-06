"""Pydantic schemas for updating a user's profile."""

from typing import Optional
from pydantic import BaseModel, Field, field_validator, ConfigDict
from app.validators.user_validators import summary_validate


class UserUpdateRequest(BaseModel):
    """
    Request schema for updating a user's profile details, including
    first and last names and an optional profile summary; all string
    fields are trimmed of surrounding whitespace.
    """
    model_config = ConfigDict(str_strip_whitespace=True)

    first_name: str = Field(..., min_length=1, max_length=40)
    last_name: str = Field(..., min_length=1, max_length=40)
    summary: Optional[str] = Field(default=None, max_length=4096)

    @field_validator("summary", mode="before")
    @classmethod
    def _validate_summary(cls, value: Optional[str]) -> Optional[str]:
        """
        Validates summary: trims whitespace and converts blank strings
        to None.
        """
        return summary_validate(value)


class UserUpdateResponse(BaseModel):
    """
    Response schema confirming a profile update by returning the unique
    identifier of the affected user account.
    """
    user_id: int
