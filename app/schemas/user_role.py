"""Pydantic schemas for managing user roles and active status."""

from typing import Literal
from pydantic import BaseModel, ConfigDict, field_validator
from app.validators.user_validators import role_validate

class UserRoleRequest(BaseModel):
    """
    Request schema for updating a user's role and active status, where
    the role value is normalized to lowercase and trimmed of whitespace
    before validation, and the active flag controls whether the user
    is enabled or not.
    """
    model_config = ConfigDict(str_strip_whitespace=True)

    role: Literal["reader", "writer", "editor", "admin"]
    active: bool

    @field_validator("role", mode="before")
    @classmethod
    def validate_role(cls, value: str) -> str:
        return role_validate(value)


class UserRoleResponse(BaseModel):
    """
    Response schema for confirming a role or active status update by
    returning the unique identifier of the affected user account.
    """
    user_id: int
