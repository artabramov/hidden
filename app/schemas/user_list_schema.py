"""
The module defines Pydantic schemas for listing users.
"""

from typing import Literal, List, Optional
from pydantic import BaseModel, Field
from app.schemas.user_select_schema import UserSelectResponse
from app.config import get_config

cfg = get_config()


class UserListRequest(BaseModel):
    """
    Request schema for listing users with pagination and filtering
    options. The order direction can be ascending, descending, or
    random.
    """
    offset: Optional[int] = Field(ge=0, default=None)
    limit: Optional[int] = Field(ge=1, default=None)
    order_by: Optional[Literal[
        "id", "username_index", "first_name_index", "last_name_index"]] = None
    order: Optional[Literal["asc", "desc", "rand"]] = None

    class Config:
        """Strips whitespaces at the beginning and end of all values."""
        str_strip_whitespace = True


class UserListResponse(BaseModel):
    """
    Response schema for listing users. Contains a list of users and
    the total count of users available.
    """
    users: List[UserSelectResponse]
    users_count: int
