# app/schemas/folder_update.py
# SPDX-License-Identifier: SSPL-1.0

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.schemas.pydantic_error import PydanticErrorResponse
from app.validators.path_segment import validate_path_segment
from app.validators.summary import normalize_summary

FOLDER_UPDATE_ERRORS = {
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
        "description": "Target folder was not found.",
    },
    409: {
        "description": (
            "A folder with the same dirname already exists in the "
            "same parent folder."
        ),
    },
    422: {
        "model": PydanticErrorResponse,
        "description": (
            "Input values failed validation (empty request body, "
            "invalid folder ID, invalid dirname length, invalid dirname "
            "value, or summary too long)."
        ),
    },
    423: {
        "description": "Target folder is write-protected.",
    },
    503: {
        "description": (
            "Service is temporarily unavailable (lockdown mode enabled "
            "or gocryptfs storage not ready)."
        ),
    },
}


class FolderUpdateRequest(BaseModel):
    """
    Request schema for updating folder metadata.

    The dirname field is required. The summary field is optional.
    Leading and trailing whitespace is stripped from string fields.
    Empty summary is normalized to null.
    """

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )

    dirname: str = Field(
        min_length=1,
        max_length=255,
        description="Updated folder directory name.",
    )

    summary: str | None = Field(
        default=None,
        max_length=4096,
        description="Updated optional folder summary.",
    )

    @field_validator("dirname")
    @classmethod
    def validate_dirname(cls, value: str) -> str:
        return validate_path_segment(value)

    @field_validator("summary")
    @classmethod
    def normalize_summary_value(cls, value: str | None) -> str | None:
        return normalize_summary(value)
