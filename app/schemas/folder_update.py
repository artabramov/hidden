"""Pydantic schemas for folder update."""

from typing import Optional
from pydantic import BaseModel, Field, field_validator, ConfigDict
from app.validators.folder_validators import summary_validate
from app.validators.file_validators import name_validate


class FolderUpdateRequest(BaseModel):
    """
    Request schema for updating a folder. Includes the read-only
    flag, folder name, and an optional summary. Whitespace is
    stripped from strings; extra fields are forbidden.
    """

    model_config = ConfigDict(
        str_strip_whitespace=True,
        extra="forbid",
    )

    readonly: bool
    name: str = Field(..., min_length=1, max_length=255)
    summary: Optional[str] = Field(default=None, max_length=4096)

    @field_validator("name")
    @classmethod
    def _validate_name(cls, v: str) -> str:
        return name_validate(v)

    @field_validator("summary")
    @classmethod
    def _validate_summary(cls, value: Optional[str]) -> Optional[str]:
        return summary_validate(value)


class FolderUpdateResponse(BaseModel):
    """
    Response schema for folder update. Contains the updated folder ID.
    """

    folder_id: int
