# app/schemas/file_update.py
# SPDX-License-Identifier: GPL-3.0-only

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.schemas.pydantic_error import PydanticErrorResponse
from app.validators.path_segment import validate_path_segment
from app.validators.summary import normalize_summary

FILE_UPDATE_ERRORS = {
    401: {
        "description": "Invalid, expired, or missing authentication token.",
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
    409: {
        "description": (
            "A file with the same name already exists in the target folder."
        ),
    },
    422: {
        "model": PydanticErrorResponse,
        "description": (
            "Input values failed validation (invalid filename or summary)."
        ),
    },
    503: {
        "description": (
            "Service is temporarily unavailable (lockdown mode enabled "
            "or gocryptfs storage not ready)."
        ),
    },
}


class FileUpdateRequest(BaseModel):
    """
    Request schema for updating file metadata.
    """

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )

    filename: str = Field(
        min_length=1,
        max_length=255,
        description="New file name.",
    )

    summary: str | None = Field(
        default=None,
        max_length=4096,
        description="Optional file summary.",
    )

    @field_validator("filename")
    @classmethod
    def validate_filename(cls, value: str) -> str:
        return validate_path_segment(value)

    @field_validator("summary")
    @classmethod
    def normalize_summary_value(cls, value: str | None) -> str | None:
        return normalize_summary(value)


class FileUpdateResponse(BaseModel):
    """
    Response schema for file update.
    """

    model_config = ConfigDict(
        extra="forbid",
        from_attributes=True,
        populate_by_name=True,
    )

    file_id: int = Field(
        validation_alias="id",
        description="Identifier of the updated file.",
    )
