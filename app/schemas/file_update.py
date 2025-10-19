"""Pydantic schemas for file update."""

from typing import Optional
from pydantic import BaseModel, Field, field_validator, ConfigDict
from app.validators.file_validators import summary_validate
from app.validators.file_validators import name_validate


class FileUpdateRequest(BaseModel):
    """
    Request schema for updating a file. Includes the required filename
    and folder ID, plus an optional summary. Whitespace is stripped from
    strings; extra fields are forbidden.
    """
    model_config = ConfigDict(
        str_strip_whitespace=True,
        extra="forbid",
    )

    folder_id: int = Field(..., ge=1)
    filename: str = Field(..., min_length=1, max_length=255)
    summary: Optional[str] = Field(default=None, max_length=4096)

    @field_validator("filename")
    @classmethod
    def _validate_filename(cls, v: str) -> str:
        return name_validate(v)

    @field_validator("summary")
    @classmethod
    def _validate_summary(cls, value: Optional[str]) -> Optional[str]:
        return summary_validate(value)


class FileUpdateResponse(BaseModel):
    """
    Response schema for file update. Contains the updated
    file ID and the latest revision number.
    """
    file_id: int
    latest_revision_number: int
