"""Pydantic schemas for user detail retrieval."""

from typing import Optional, Literal
from pydantic import BaseModel


class UserSelectResponse(BaseModel):
    """
    Response schema for user detail retrieval. Includes the user ID;
    creation and last-login timestamps (Unix seconds, UTC); role
    (reader, writer, editor, admin); active status; username; first
    and last name; optional summary; and a flag indicating whether
    a user thumbnail exists.
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
