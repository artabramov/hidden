# app/schemas/user_totp_recover.py
# SPDX-License-Identifier: GPL-3.0-only

from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, StringConstraints

from app.schemas.pydantic_error import PydanticErrorResponse

USER_TOTP_RECOVER_ERRORS = {
    409: {
        "description": (
            "Password verification step was not completed or has expired "
            "before recovery-code verification."
        ),
    },
    422: {
        "model": PydanticErrorResponse,
        "description": (
            "Input validation failed or recovery authentication failed."
        ),
    },
    503: {
        "description": (
            "Service is temporarily unavailable (lockdown mode enabled "
            "or gocryptfs storage not ready)."
        ),
    },
}


class UserTotpRecoverRequest(BaseModel):
    """MFA session UUID plus recovery code (alternate second auth step)."""

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )

    mfa_session_uuid: Annotated[
        str,
        StringConstraints(
            min_length=20,
            max_length=80,
        ),
    ] = Field(
        description="MFA session UUID from the password login step.",
    )

    recovery_code: Annotated[
        str,
        StringConstraints(
            min_length=8,
            max_length=40,
        ),
    ] = Field(
        description="Account recovery code from registration.",
    )


class UserTotpRecoverResponse(BaseModel):
    """New TOTP secret after successful recovery (no JWT issued)."""

    model_config = ConfigDict(
        extra="forbid",
    )

    user_id: int = Field(
        description="User whose TOTP secret was rotated.",
    )

    totp_secret: str = Field(
        description="New TOTP secret for authenticator setup.",
    )
