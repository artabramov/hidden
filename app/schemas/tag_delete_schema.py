"""
The module defines Pydantic schemas for deleting a document tag.
"""

from typing import Optional
from pydantic import BaseModel, Field, field_validator
from app.validators.tag_value_validator import tag_value_validate


class TagDeleteRequest(BaseModel):
    """
    Request schema for deleting a document tag. The tag value
    is validated and cleaned before being processed.
    """
    tag_value: str = Field(..., min_length=1, max_length=47)

    class Config:
        """Strips whitespaces at the beginning and end of all values."""
        str_strip_whitespace = True

    @field_validator("tag_value", mode="before")
    def validate_tag_value(
            cls, tag_value: Optional[str]) -> Optional[str]:
        """Validates tag value."""
        return tag_value_validate(tag_value)


class TagDeleteResponse(BaseModel):
    """
    Response schema for a successful tag deletions. It contains
    the unique identifier for the deleted tag.
    """
    tag_id: int
