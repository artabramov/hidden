# app/schemas/user_password_change.py
# SPDX-License-Identifier: GPL-3.0-only

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.schemas.pydantic_error import PydanticErrorResponse
from app.validators.password import validate_password

USER_PASSWORD_CHANGE_ERRORS = {
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
            "current password does not match the stored password, "
            "invalid current password length, or invalid new password "
            "length or strength)."
        ),
    },
    503: {
        "description": (
            "Service is temporarily unavailable (lockdown mode enabled "
            "or gocryptfs storage not ready)."
        ),
    },
}


class UserPasswordChangeRequest(BaseModel):
    """
    Request schema for changing user password with validation of
    current and updated passwords.
    """

    model_config = ConfigDict(
        extra="forbid",
    )

    current_password: str = Field(
        min_length=8,
        description="Current password used for authentication.",
    )

    changed_password: str = Field(
        min_length=8,
        description="New password to replace the current one.",
    )

    @field_validator("changed_password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        return validate_password(value)
