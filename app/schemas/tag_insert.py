"""Pydantic schemas for file tag insertion."""

from pydantic import BaseModel, ConfigDict, Field, field_validator
from app.validators.tag_validators import value_validate


class TagInsertRequest(BaseModel):
    """
    Request schema for creating a new file tag. The tag value
    is validated and cleaned before being processed.
    """
    model_config = ConfigDict(
        str_strip_whitespace=True,
        extra="forbid",
    )

    value: str = Field(..., min_length=1, max_length=40)

    @field_validator("value", mode="before")
    def validate_value(cls, value: str) -> str:
        """Validate and normalize tag value."""
        return value_validate(value)


class TagInsertResponse(BaseModel):
    """
    Response schema for tag insert. Contains the related
    file ID and the latest revision number.
    """
    file_id: int
    latest_revision_number: int
