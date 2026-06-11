# app/schemas/user_select.py
# SPDX-License-Identifier: GPL-3.0-only

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.pydantic_error import PydanticErrorResponse

USER_SELECT_ERRORS = {
    401: {
        "description": (
            "Invalid, expired, or missing authentication token."
        ),
    },
    403: {
        "description": (
            "Authenticated user is inactive, blocked, lacks required "
            "permissions, or attempted to access another user's record."
        ),
    },
    404: {
        "description": "Target user was not found.",
    },
    422: {
        "model": PydanticErrorResponse,
        "description": (
            "Input values failed validation (e.g. non-integer user ID "
            "in the path)."
        ),
    },
    503: {
        "description": (
            "Service is temporarily unavailable (lockdown mode enabled "
            "or gocryptfs storage not ready)."
        ),
    },
}


class UserSelectResponse(BaseModel):
    """
    Response schema for user selection containing account metadata,
    authentication timestamps, role, status, and public profile fields.
    """

    model_config = ConfigDict(
        extra="forbid",
        from_attributes=True,
        populate_by_name=True,
    )

    user_id: int = Field(
        validation_alias="id",
        description="Identifier of the user.",
    )

    created_at: int = Field(
        description="Timestamp when the user account was created.",
    )

    last_authenticated_at: int | None = Field(
        default=None,
        description="Timestamp of the last successful authentication.",
    )

    role: str = Field(
        description="Role assigned to the user.",
    )

    is_active: bool = Field(
        description="Activation status of the user.",
    )

    username: str = Field(
        description="Username used for authentication.",
    )

    display_name: str = Field(
        description="Public display name of the user.",
    )

    summary: str | None = Field(
        default=None,
        description="Optional user profile summary.",
    )
