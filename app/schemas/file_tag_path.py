# app/schemas/file_tag_path.py
# SPDX-License-Identifier: GPL-3.0-only

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.validators.file_tag import validate_file_tag


class FileTagPath(BaseModel):
    """
    Path parameters identifying a file tag. Leading and trailing
    whitespace is stripped from the tag value.
    """

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )

    file_id: int = Field(
        gt=0,
        description="ID of the target file.",
    )

    tag: str = Field(
        min_length=1,
        max_length=64,
        description="Tag value attached to the file.",
    )

    @field_validator("tag")
    @classmethod
    def validate_tag(cls, value: object) -> str:
        return validate_file_tag(value)
