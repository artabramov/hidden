"""
The module defines Pydantic schemas for selecting and retrieving user
details.
"""

from typing import Optional, Literal
from pydantic import BaseModel


class UserSelectResponse(BaseModel):
    """
    Response schema for selecting a user's details. Contains information
    about a user, including their unique identifier, creation date,
    username, first and last names, role within the app, active status,
    and optional fields like user summary and profile picture URL. This
    schema is used to return user details when querying the user record.
    """
    id: int
    created_date: int
    username: str
    first_name: str
    last_name: str
    user_role: Literal["reader", "writer", "editor", "admin"]
    is_active: bool
    user_summary: Optional[str] = None
    userpic_filename: Optional[str] = None
    user_meta: dict
