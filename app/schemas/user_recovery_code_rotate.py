# app/schemas/user_recovery_code_rotate.py
# SPDX-License-Identifier: SSPL-1.0

from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, StringConstraints

from app.schemas.pydantic_error import PydanticErrorResponse

USER_RECOVERY_CODE_ROTATE_ERRORS = {
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
            "invalid recovery code length or format, or submitted recovery "
            "code does not match the stored hash)."
        ),
    },
    503: {
        "description": (
            "Service is temporarily unavailable (lockdown mode enabled "
            "or gocryptfs storage not ready)."
        ),
    },
}


class UserRecoveryCodeRotateRequest(BaseModel):
    """
    Request to rotate the account recovery code after verifying the
    existing recovery code. The new recovery code is generated
    server-side and returned in the response body once.
    """

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )

    recovery_code: Annotated[
        str,
        StringConstraints(
            min_length=8,
            max_length=40,
        ),
    ] = Field(
        description="Current account recovery code before rotation.",
    )


class UserRecoveryCodeRotateResponse(BaseModel):
    """New recovery code after successful rotation (store offline)."""

    model_config = ConfigDict(
        extra="forbid",
    )

    recovery_code: str = Field(
        description=(
            "New recovery code; shown only in this response. "
            "The server stores only a hash."
        ),
    )
