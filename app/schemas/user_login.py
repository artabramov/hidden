"""Pydantic schemas for user login."""

from pydantic import BaseModel, Field, SecretStr, ConfigDict, field_validator
from app.validators.user_validators import username_validate


class UserLoginRequest(BaseModel):
    """
    Request schema for user login. Carries the username and password
    used to authenticate the account; the username is trimmed and
    lowercased (Latin letters, digits, underscore).
    """
    model_config = ConfigDict(str_strip_whitespace=True)

    username: str = Field(...)
    password: SecretStr = Field(...)

    @field_validator("username", mode="before")
    @classmethod
    def _validate_username(cls, value: str) -> str:
        """Validates username: strips, lowercases and [a-z0-9_] only."""
        return username_validate(value)


class UserLoginResponse(BaseModel):
    """
    Response schema for user login. Returns the user ID and a flag
    indicating that the password step was accepted and the flow may
    proceed to MFA.
    """
    user_id: int
    password_accepted: bool
