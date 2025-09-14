"""Pydantic schemas for updating a document."""

from typing import Optional
from pydantic import BaseModel, Field, field_validator, ConfigDict
from app.validators.user_validators import summary_validate
from app.validators.file_validators import name_validate


class DocumentUpdateRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    filename: Optional[str] = Field(default=None, min_length=1, max_length=255)
    collection_id: Optional[int] = Field(default=None, ge=1)
    summary: Optional[str] = Field(default=None, max_length=4096)

    @field_validator("filename")
    @classmethod
    def _validate_filename(cls, v: str) -> str:
        return name_validate(v)

    @field_validator("summary", mode="before")
    @classmethod
    def _validate_summary(cls, value: Optional[str]) -> Optional[str]:
        """
        Validates document summary: trims whitespace
        and converts blank strings to None.
        """
        return summary_validate(value)


class DocumentUpdateResponse(BaseModel):
    document_id: int
    latest_revision_number: int
