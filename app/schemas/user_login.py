# app/schemas/user_login.py
# SPDX-License-Identifier: SSPL-1.0

from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, StringConstraints

from app.schemas.pydantic_error import PydanticErrorResponse

USER_LOGIN_ERRORS = {
    422: {
        "model": PydanticErrorResponse,
        "description": (
            "Input values failed validation (missing required fields, "
            "username not found, invalid password, invalid username "
            "length, or invalid password length; authentication failures "
            "may be intentionally returned in a generic form to prevent "
            "timing-based username enumeration)."
        ),
    },
    503: {
        "description": (
            "Service is temporarily unavailable (lockdown mode enabled "
            "or gocryptfs storage not ready)."
        ),
    },
}


# NOTE (ADR-34): Secondary Pydantic schemas avoid duplicating validation.
# Complex validation rules are applied in primary Pydantic schemas
# (e.g., registration) and are not repeated in secondary schemas
# (e.g., login). This prevents divergence of validation logic for the
# same field across different request schemas.

class UserLoginRequest(BaseModel):
    """
    Request schema for user login with validation of username and
    password. Username is normalized to lowercase. Leading and trailing
    whitespace is stripped from non-secret string fields only.
    """

    model_config = ConfigDict(
        extra="forbid",
    )

    username: Annotated[
        str,
        StringConstraints(
            strip_whitespace=True,
            to_lower=True,
            min_length=4,
            max_length=40,
        ),
    ] = Field(
        description="Username used for authentication.",
    )

    password: Annotated[
        str,
        StringConstraints(
            min_length=8,
            strip_whitespace=False,
        ),
    ] = Field(
        description="Password used for authentication.",
    )


class UserLoginResponse(BaseModel):
    """
    Response schema for MFA session initialization containing the
    temporary session UUID used for second-factor verification.
    """

    model_config = ConfigDict(
        extra="forbid",
    )

    mfa_session_uuid: str = Field(
        min_length=20,
        max_length=80,
        description="MFA session UUID used for second-factor verification.",
    )
