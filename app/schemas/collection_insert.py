from typing import Optional
from pydantic import BaseModel, Field, ConfigDict, field_validator
from app.validators.collection_validators import summary_validate
from app.validators.file_validators import name_validate


class CollectionInsertRequest(BaseModel):
    """Pydantic schema for inserting a collection."""

    model_config = ConfigDict(
        str_strip_whitespace=True,
        extra="forbid",
    )

    readonly: bool = False
    name: str = Field(..., min_length=1, max_length=256)
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
    """Pydantic schema for collection insert response."""

    collection_id: int = Field(..., ge=1)
