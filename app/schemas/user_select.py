"""Pydantic schemas for user detail retrieval."""

from typing import Optional, Literal
from pydantic import BaseModel


class UserSelectResponse(BaseModel):
    """
    Response schema for user details. Includes identifiers, creation
    and last-login timestamps, role, active status, username, first/last
    name, optional summary, and thumbnail presence flag.
    """

    id: int
    created_date: int
    last_login_date: int
    role: Literal["reader", "writer", "editor", "admin"]
    active: bool
    username: str
    first_name: str
    last_name: str
    summary: Optional[str] = None
    has_thumbnail: bool
