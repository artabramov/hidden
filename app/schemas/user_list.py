"""Pydantic schemas for listing users."""

from typing import Optional, List, Literal
from pydantic import BaseModel, Field, ConfigDict
from app.schemas.user_select import UserSelectResponse


class UserListRequest(BaseModel):
    """
    Request schema for retrieving a paginated list of users with
    optional filters and ordering; string filter fields are trimmed
    of surrounding whitespace.
    """
    model_config = ConfigDict(str_strip_whitespace=True)

    active__eq: Optional[bool] = None
    role__eq: Optional[Literal["reader", "writer", "editor", "admin"]] = None
    username__ilike: Optional[str] = None
    first_name__ilike: Optional[str] = None
    last_name__ilike: Optional[str] = None
    full_name__ilike: Optional[str] = None
    offset: int = Field(..., ge=0)
    limit: int = Field(..., ge=1, le=200)
    order_by: Literal[
        "id",
        "created_date",
        "last_login_date",
        "role",
        "active",
        "username",
        "first_name",
        "last_name",
        "full_name"
    ]
    order: Literal["asc", "desc", "rand"]


class UserListResponse(BaseModel):
    """
    Response schema with the user list matching the criteria and the
    total count of matched users.
    """
    users: List[UserSelectResponse]
    users_count: int
