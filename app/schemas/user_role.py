"""Pydantic schemas for user role update."""

from typing import Literal
from pydantic import BaseModel, ConfigDict, field_validator
from app.validators.user_validators import role_validate


class UserRoleRequest(BaseModel):
    """
    Request schema for updating a user's role and active status.
    Includes the new role (reader|writer|editor|admin) and an activity
    status. Whitespace is stripped from strings. Extra fields are
    forbidden.
    """
    model_config = ConfigDict(
        str_strip_whitespace=True,
        extra="forbid",
    )

    role: Literal["reader", "writer", "editor", "admin"]
    active: bool

    @field_validator("role")
    @classmethod
    def validate_role(cls, value: str) -> str:
        return role_validate(value)


class UserRoleResponse(BaseModel):
    """
    Response schema for user role update. Contains the user ID.
    """
    user_id: int
