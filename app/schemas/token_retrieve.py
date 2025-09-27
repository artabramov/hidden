"""Pydantic schemas for token retrieval."""

from typing import Optional
from pydantic import BaseModel, Field, ConfigDict, field_validator
from app.validators.user_validators import username_validate, totp_validate


class TokenRetrieveRequest(BaseModel):
    """
    Request schema for token retrieval. Includes the username,
    a time-based one-time password (TOTP), and an optional token
    lifetime exp — absolute expiration timestamp in Unix seconds;
    if omitted, the token is issued without an exp claim (non-expiring).
    Extra fields are forbidden.
    """

    model_config = ConfigDict(
        str_strip_whitespace=True,
        extra="forbid",
    )

    username: str = Field(...)
    totp: str = Field(..., min_length=6, max_length=6)
    exp: Optional[int] = Field(default=None, ge=1)

    @field_validator("totp")
    @classmethod
    def _validate_totp(cls, totp: str) -> str:
        return totp_validate(totp)


class TokenRetrieveResponse(BaseModel):
    """
    Response schema for token retrieval. Returns the user ID and
    a signed JWT access token for authenticated requests.
    """

    user_id: int
    user_token: str
