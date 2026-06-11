# app/schemas/user_token_issue.py
# SPDX-License-Identifier: GPL-3.0-only

from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, StringConstraints

from app.schemas.pydantic_error import PydanticErrorResponse

USER_TOKEN_ISSUE_ERRORS = {
    409: {
        "description": (
            "Password verification step was not completed or has expired "
            "before MFA second-factor verification."
        ),
    },
    422: {
        "model": PydanticErrorResponse,
        "description": (
            "Input values failed validation (missing required fields, "
            "invalid MFA session UUID, or invalid TOTP code; "
            "authentication failures may be intentionally returned in "
            "a generic form to prevent information disclosure)."
        ),
    },
    503: {
        "description": (
            "Service is temporarily unavailable (lockdown mode enabled "
            "or gocryptfs storage not ready)."
        ),
    },
}


class TokenIssueRequest(BaseModel):
    """
    Request schema for token issuance with validation of MFA session
    UUID and TOTP code. Leading and trailing whitespace is stripped
    from non-secret string fields.
    """

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
        description="MFA session UUID obtained from the login step.",
    )

    totp: Annotated[
        str,
        StringConstraints(
            pattern=r"^\d{6}$",
            min_length=6,
            max_length=6,
        ),
    ] = Field(
        description="TOTP code used for multi-factor authentication.",
    )

    disable_exp: bool = Field(
        default=False,
        description=(
            "When true and the server allows tokens without expiration, "
            "issues a token without an expiration date. Ignored when "
            "the server setting is disabled."
        ),
    )


class TokenIssueResponse(BaseModel):
    """
    Response schema for token issuance containing the authenticated
    user identifier and the issued authentication token.
    """

    model_config = ConfigDict(
        extra="forbid",
    )

    user_id: int = Field(
        description="Identifier of the authenticated user.",
    )

    auth_token: str = Field(
        description="Issued authentication token.",
    )
