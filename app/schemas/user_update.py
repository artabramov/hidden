# app/schemas/user_update.py
# SPDX-License-Identifier: SSPL-1.0

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.schemas.pydantic_error import PydanticErrorResponse
from app.validators.summary import normalize_summary

USER_UPDATE_ERRORS = {
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
    422: {
        "model": PydanticErrorResponse,
        "description": (
            "Input values failed validation (missing required fields, "
            "invalid display name length, or summary too long)."
        ),
    },
    503: {
        "description": (
            "Service is temporarily unavailable (lockdown mode enabled "
            "or gocryptfs storage not ready)."
        ),
    },
}


class UserUpdateRequest(BaseModel):
    """
    Request schema for updating current user profile with validation of
    display name and optional summary. Leading and trailing whitespace
    is stripped from string fields.
    """

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )

    display_name: str = Field(
        min_length=4,
        max_length=40,
        description="Updated public display name of the user.",
    )

    summary: str | None = Field(
        default=None,
        max_length=4096,
        description="Updated optional user profile summary.",
    )

    @field_validator("summary")
    @classmethod
    def normalize_summary(cls, value: str | None) -> str | None:
        return normalize_summary(value)
