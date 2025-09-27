"""Pydantic schemas for user login."""

from pydantic import BaseModel, Field, SecretStr, ConfigDict, field_validator
from app.validators.user_validators import username_validate


class UserLoginRequest(BaseModel):
    """
    Request schema for user login. Carries the username and password
    used to authenticate the account; the username is trimmed and
    lowercased (Latin letters, digits, underscore). Extra fields
    are forbidden.
    """

    model_config = ConfigDict(
        str_strip_whitespace=True,
        extra="forbid",
    )

    username: str = Field(...)
    password: SecretStr = Field(...)


class UserLoginResponse(BaseModel):
    """
    Response schema for user login. Returns the user ID and a flag
    indicating that the password step was accepted and the flow may
    proceed to MFA.
    """

    user_id: int
    password_accepted: bool
