"""
The module defines Pydantic schemas for the creation and response of
collections.
"""

from typing import Optional
from pydantic import BaseModel, Field, field_validator
from app.validators.collection_summary_validator import (
    collection_summary_validate)


class CollectionInsertRequest(BaseModel):
    """
    Request schema for creating a new collection. It includes the
    collection name, which must be between 2 and 79 characters, and
    an optional summary for the collection, which can be up to 1023
    characters. The fields are validated and cleaned before being
    processed.
    """
    collection_name: str = Field(..., min_length=1, max_length=79)
    collection_summary: Optional[str] = Field(max_length=4095, default=None)

    class Config:
        """Strips whitespaces at the beginning and end of all values."""
        str_strip_whitespace = True

    @field_validator("collection_summary", mode="before")
    def validate_collection_summary(
            cls, collection_summary: Optional[str]) -> Optional[str]:
        return collection_summary_validate(collection_summary)


class CollectionInsertResponse(BaseModel):
    """
    Response schema for a successful collection creation. It contains
    the unique identifier for the newly created collection.
    """
    collection_id: int
