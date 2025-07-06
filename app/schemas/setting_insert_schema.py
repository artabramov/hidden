"""
The module defines Pydantic schemas for managing and updating settings.
"""

from typing import Optional
from pydantic import BaseModel, Field, field_validator


class SettingInsertRequest(BaseModel):
    """
    Request schema for updating a setting value.
    """
    setting_key: str = Field(..., min_length=1, max_length=47)
    setting_value: Optional[str] = Field(default=None)

    class Config:
        """Strips whitespaces at the beginning and end of all values."""
        str_strip_whitespace = True

    @field_validator("setting_key", mode="before")
    def validate_setting_key(cls, setting_key: str) -> str:
        return setting_key.lower()


class SettingInsertResponse(BaseModel):
    """
    Response schema for a successful setting updation.
    """
    setting_key: str
