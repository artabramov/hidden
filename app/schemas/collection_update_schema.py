"""
The module defines Pydantic schemas for updating a collection's
information.
"""

from typing import Optional
from pydantic import BaseModel, Field, field_validator
from app.validators.collection_summary_validator import (
    collection_summary_validate)


class CollectionUpdateRequest(BaseModel):
    """
    Request schema for updating a collection. It includes the collection
    name, and an optional summary for the collection.
    """
    collection_name: str = Field(..., min_length=2, max_length=79)
    collection_summary: Optional[str] = Field(max_length=4095, default=None)

    class Config:
        """Strips whitespaces at the beginning and end of all values."""
        str_strip_whitespace = True

    @field_validator("collection_summary", mode="before")
    def validate_collection_summary(
            cls, collection_summary: Optional[str]) -> Optional[str]:
        """Validates collection summary."""
        return collection_summary_validate(collection_summary)


class CollectionUpdateResponse(BaseModel):
    """
    Response schema for a successful collection updation. It contains
    the unique identifier for the updated collection.
    """
    collection_id: int
