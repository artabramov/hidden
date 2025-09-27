"""Pydantic schemas for collection insertion."""

from typing import Optional
from pydantic import BaseModel, Field, ConfigDict, field_validator
from app.validators.collection_validators import summary_validate
from app.validators.file_validators import name_validate


class CollectionInsertRequest(BaseModel):
    """
    Request schema for collection insertion. Includes the read-only
    flag, collection name, and an optional summary. Whitespace is
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
    def _validate_summary(cls, v: Optional[str]) -> Optional[str]:
        return summary_validate(v)


class CollectionInsertResponse(BaseModel):
    """
    Response schema for collection insertion. Contains the created
    collection ID.
    """

    collection_id: int
