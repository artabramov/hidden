"""Pydantic schemas for updating a collection."""

from typing import Optional
from pydantic import BaseModel, Field, field_validator, ConfigDict
from app.validators.collection_validators import summary_validate
from app.validators.file_validators import name_validate


class CollectionUpdateRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    name: Optional[str] = Field(default=None, min_length=1, max_length=255)
    summary: Optional[str] = Field(default=None, max_length=4096)

    @field_validator("name")
    @classmethod
    def _validate_name(cls, v: str) -> str:
        return name_validate(v)

    @field_validator("summary", mode="before")
    @classmethod
    def _validate_summary(cls, value: Optional[str]) -> Optional[str]:
        """
        Validates collection summary: trims whitespace
        and converts blank strings to None.
        """
        return summary_validate(value)


class CollectionUpdateResponse(BaseModel):
    collection_id: int
