"""
The module defines Pydantic schemas for changing a user's role and
activity status.
"""

from typing import Literal
from pydantic import BaseModel


class UserRoleRequest(BaseModel):
    """
    Request schema for updating a user's role and activity status.
    Contains the new role for the user and a boolean flag indicating
    whether the user is active or not. The user role must be one
    of the following: "reader", "writer", "editor", or "admin".
    """
    user_role: Literal["reader", "writer", "editor", "admin"]
    is_active: bool


class UserRoleResponse(BaseModel):
    """
    Response schema for the successful update of a user's role. Contains
    the user's unique identifier that confirms the update was applied to
    the specific user.
    """
    user_id: int
