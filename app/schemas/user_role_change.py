# app/schemas/user_role_change.py
# SPDX-License-Identifier: GPL-3.0-only

from pydantic import BaseModel, ConfigDict, Field

from app.models.user import UserRole
from app.schemas.pydantic_error import PydanticErrorResponse

USER_ROLE_CHANGE_ERRORS = {
    401: {
        "description": (
            "Invalid, expired, or missing authentication token."
        ),
    },
    403: {
        "description": (
            "Access denied (inactive or suspended user, insufficient "
            "permissions, or admin attempted self role/status update)."
        ),
    },
    404: {
        "description": "User was not found.",
    },
    422: {
        "model": PydanticErrorResponse,
        "description": (
            "Input values failed validation (non-integer user ID, "
            "missing required fields, invalid role value, or invalid "
            "active-status value)."
        ),
    },
    503: {
        "description": (
            "Service is temporarily unavailable (lockdown mode enabled "
            "or gocryptfs storage not ready)."
        ),
    },
}


class UserRoleChangeRequest(BaseModel):
    """
    Request schema for changing a user's role and activation status.
    Leading and trailing whitespace is stripped from string fields.
    """

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )

    role: UserRole = Field(
        description="New role assigned to the target user.",
    )

    is_active: bool = Field(
        description="Whether the target user is active or not.",
    )
