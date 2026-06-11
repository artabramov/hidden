# app/schemas/file_tag_add.py
# SPDX-License-Identifier: GPL-3.0-only

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.schemas.pydantic_error import PydanticErrorResponse
from app.validators.file_tag import validate_file_tag

FILE_TAG_ADD_ERRORS = {
    401: {
        "description": (
            "Invalid, expired, or missing authentication token."
        ),
    },
    403: {
        "description": (
            "Authenticated user is inactive, blocked, or lacks "
            "required permissions."
        ),
    },
    404: {
        "description": "Target file was not found.",
    },
    422: {
        "model": PydanticErrorResponse,
        "description": (
            "Input values failed validation (invalid file ID, missing "
            "tag, empty tag, tag too long, invalid tag format, or "
            "extra fields)."
        ),
    },
    423: {
        "description": "Parent folder is write-protected.",
    },
    503: {
        "description": (
            "Service is temporarily unavailable (lockdown mode enabled "
            "or gocryptfs storage not ready)."
        ),
    },
}


class FileTagAddRequest(BaseModel):
    """
    Request schema for adding a tag to a file. Leading and trailing
    whitespace is stripped from the tag value.
    """

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )

    tag: str = Field(
        min_length=1,
        max_length=64,
        description="Tag value to attach to the file.",
    )

    @field_validator("tag")
    @classmethod
    def validate_tag(cls, value: object) -> str:
        return validate_file_tag(value)
