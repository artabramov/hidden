"""
The module defines Pydantic schemas for document update operations.
"""

from typing import Optional, Union
from pydantic import BaseModel, Field, field_validator
from app.validators.document_summary_validator import document_summary_validate


class DocumentUpdateRequest(BaseModel):
    """
    Request schema for updating a document. It includes the original
    filename, and an optional document summary, and collection ID. The
    fields are validated and cleaned before being processed.
    """
    original_filename: str = Field(..., min_length=1, max_length=255)
    document_summary: Optional[str] = Field(max_length=4095, default=None)
    collection_id: Optional[int] = None

    class Config:
        """Strips whitespaces at the beginning and end of all values."""
        str_strip_whitespace = True

    @field_validator("document_summary", mode="before")
    def validate_document_summary(
            cls, document_summary: Optional[str]) -> Union[str, None]:
        """Validates document summary."""
        return document_summary_validate(document_summary)


class DocumentUpdateResponse(BaseModel):
    """
    Response schema for a successful document updation. It contains
    the unique identifier for the updated document.
    """
    document_id: int
