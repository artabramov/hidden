"""Pydantic schemas for listing users."""

from typing import Optional, List, Literal
from pydantic import BaseModel, Field, ConfigDict
from app.schemas.user_select import UserSelectResponse


class UserListRequest(BaseModel):
    """
    Request schema for listing users. Allows filtering by activity
    status and role; by username (case-insensitive); by name fields:
    first_name, last_name, full_name (case-insensitive); and by
    creation/last-login time ranges. Supports pagination via
    offset/limit. Results can be ordered by id, created_date,
    last_login_date, role, active, username, first_name, last_name,
    or full_name in ascending, descending, or random order.
    """

    model_config = ConfigDict(
        str_strip_whitespace=True
    )

    created_date__ge: Optional[int] = Field(default=None, ge=0)
    created_date__le: Optional[int] = Field(default=None, ge=0)
    last_login_date__ge: Optional[int] = Field(default=None, ge=0)
    last_login_date__le: Optional[int] = Field(default=None, ge=0)
    active__eq: Optional[bool] = None
    role__eq: Optional[Literal["reader", "writer", "editor", "admin"]] = None
    username__ilike: Optional[str] = None
    first_name__ilike: Optional[str] = None
    last_name__ilike: Optional[str] = None
    full_name__ilike: Optional[str] = None
    offset: int = Field(default=0, ge=0)
    limit: int = Field(default=50, ge=1, le=500)
    order_by: Literal[
        "id", "created_date", "last_login_date", "role", "active",
        "username", "first_name", "last_name", "full_name"] = "id"
    order: Literal["asc", "desc", "rand"] = "desc"


class UserListResponse(BaseModel):
    """
    Response schema for listing users. Contains the selected page
    of users and the total number of matches before pagination.
    """

    users: List[UserSelectResponse]
    users_count: int
