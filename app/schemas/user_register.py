# app/schemas/user_register.py
# SPDX-License-Identifier: SSPL-1.0

import re
from typing import Annotated

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    StringConstraints,
    field_validator,
)
from pydantic_core import PydanticCustomError

from app.schemas.pydantic_error import PydanticErrorResponse
from app.validators.password import validate_password
from app.validators.summary import normalize_summary
from app.validators.validation_errors import VALUE_NOT_LATIN_EXTENDED

USER_REGISTER_ERRORS = {
    422: {
        "model": PydanticErrorResponse,
        "description": (
            "Input values failed validation (missing required fields, "
            "username already exists, invalid username length or format, "
            "invalid password length or strength, invalid display name "
            "length, or summary too long)."
        ),
    },
    429: {
        "description": (
            "Too many registration attempts within a short time period."
        ),
    },
    503: {
        "description": (
            "Service is temporarily unavailable (lockdown mode enabled "
            "or gocryptfs storage not ready)."
        ),
    },
}


class UserRegisterRequest(BaseModel):
    """
    Request schema for user registration request with validation of
    username, password, display name, and optional profile summary.
    Username is normalized to lowercase. Leading and trailing
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
        description="Unique username used for authentication.",
    )

    password: str = Field(
        min_length=8,
        description="Password used for account authentication.",
    )

    display_name: Annotated[
        str,
        StringConstraints(
            min_length=4,
            max_length=40,
            strip_whitespace=True,
        ),
    ] = Field(
        description="Public display name of the user.",
    )

    summary: Annotated[
        str,
        StringConstraints(
            max_length=4096,
            strip_whitespace=True,
        ),
    ] | None = Field(
        default=None,
        description="Optional user profile summary.",
    )

    @field_validator("username")
    @classmethod
    def validate_username(cls, value: str) -> str:
        if not re.fullmatch(r"^[A-Za-z0-9_-]+$", value):
            raise PydanticCustomError(*VALUE_NOT_LATIN_EXTENDED)
        return value

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        return validate_password(value)

    @field_validator("summary")
    @classmethod
    def normalize_summary(cls, value: str | None) -> str | None:
        return normalize_summary(value)


class UserRegisterResponse(BaseModel):
    """
    Response schema for user registration containing the created
    user identifier, the TOTP secret for initial MFA setup, and a
    one-time recovery code (store securely; only shown in this response).
    """

    model_config = ConfigDict(
        extra="forbid",
    )

    user_id: int = Field(
        description="Identifier of the created user.",
    )

    totp_secret: str = Field(
        description="TOTP secret used for initial MFA setup.",
    )

    recovery_code: str = Field(
        description=(
            "Recovery code for account access if TOTP is unavailable; "
            "stored server-side only as a hash."
        ),
    )
