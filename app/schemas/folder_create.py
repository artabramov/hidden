# app/schemas/folder_create.py
# SPDX-License-Identifier: SSPL-1.0

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.schemas.pydantic_error import PydanticErrorResponse
from app.validators.path_segment import validate_path_segment
from app.validators.summary import normalize_summary

FOLDER_CREATE_ERRORS = {
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
        "description": "Parent folder was not found.",
    },
    409: {
        "description": (
            "A folder with the same dirname already exists in the "
            "target parent."
        ),
    },
    422: {
        "model": PydanticErrorResponse,
        "description": (
            "Input values failed validation (missing required fields, "
            "invalid parent_id, invalid dirname length, or summary too "
            "long)."
        ),
    },
    423: {
        "description": "Target parent folder is write-protected.",
    },
    503: {
        "description": (
            "Service is temporarily unavailable (lockdown mode enabled "
            "or gocryptfs storage not ready)."
        ),
    },
}


class FolderCreateRequest(BaseModel):
    """
    Request schema for folder creation with validation of optional
    parent folder identifier, directory name, and optional summary.
    Leading and trailing whitespace is stripped from string fields.
    Empty summary is normalized to null.
    """
    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )

    parent_id: int | None = Field(
        default=None,
        ge=1,
        description="Identifier of the parent folder. Null means the root.",
    )

    dirname: str = Field(
        min_length=1,
        max_length=255,
        description="Name of the new folder.",
    )

    summary: str | None = Field(
        default=None,
        max_length=4096,
        description="Optional folder summary.",
    )

    @field_validator("dirname")
    @classmethod
    def validate_dirname(cls, value: str) -> str:
        return validate_path_segment(value)

    @field_validator("summary")
    @classmethod
    def normalize_summary_value(cls, value: str | None) -> str | None:
        return normalize_summary(value)


class FolderCreateResponse(BaseModel):
    """
    Response schema for folder creation containing the created folder
    identifier.
    """

    model_config = ConfigDict(
        extra="forbid",
        from_attributes=True,
    )

    folder_id: int = Field(
        validation_alias="id",
        description="Identifier of the created folder.",
    )
