# app/schemas/user_list.py
# SPDX-License-Identifier: GPL-3.0-only

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.pydantic_error import PydanticErrorResponse
from app.schemas.user_select import UserSelectResponse

OrderByField = Literal[
    "id",
    "created_at",
    "last_authenticated_at",
    "role",
    "is_active",
    "username",
    "display_name",
]


USER_LIST_ERRORS = {
    401: {
        "description": (
            "Invalid, expired, or missing authentication token."
        ),
    },
    403: {
        "description": (
            "Authenticated user is not an admin, inactive, or blocked."
        ),
    },
    422: {
        "model": PydanticErrorResponse,
        "description": (
            "Input values failed validation (negative timestamps, "
            "invalid role or ordering values, or invalid offset / limit)."
        ),
    },
    503: {
        "description": (
            "Service is temporarily unavailable (lockdown mode enabled "
            "or gocryptfs storage not ready)."
        ),
    },
}


class UserListRequest(BaseModel):
    """
    Request schema for querying users with filtering by timestamps,
    role, status, and text search, as well as pagination and ordering.
    Extra fields are forbidden. Leading and trailing whitespace is
    stripped from string fields.
    """

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )

    created_at__ge: int | None = Field(
        default=None,
        ge=0,
        description="Lower bound for user creation timestamp.",
    )

    created_at__le: int | None = Field(
        default=None,
        ge=0,
        description="Upper bound for user creation timestamp.",
    )

    last_authenticated_at__ge: int | None = Field(
        default=None,
        ge=0,
        description="Lower bound for last authentication timestamp.",
    )

    last_authenticated_at__le: int | None = Field(
        default=None,
        ge=0,
        description="Upper bound for last authentication timestamp.",
    )

    is_active__eq: bool | None = Field(
        default=None,
        description="Filter by user activation status.",
    )

    role__eq: Literal["reader", "writer", "editor", "admin"] | None = Field(
        default=None,
        description="Filter by user role.",
    )

    username__ilike: str | None = Field(
        default=None,
        description="Case-insensitive substring match for username.",
    )

    display_name__ilike: str | None = Field(
        default=None,
        description="Case-insensitive substring match for display name.",
    )

    offset: int = Field(
        default=0,
        ge=0,
        description="Number of records to skip for pagination.",
    )

    limit: int = Field(
        default=50,
        ge=1,
        le=500,
        description="Maximum number of records to return.",
    )

    order_by: OrderByField = Field(
        default="id",
        description="Field used for result ordering.",
    )

    order: Literal["asc", "desc", "rand"] = Field(
        default="desc",
        description="Ordering direction or random ordering.",
    )


class UserListResponse(BaseModel):
    """
    Response schema for user listing containing matched user records
    and the total number of users satisfying the query conditions.
    """

    model_config = ConfigDict(
        extra="forbid",
    )

    users: list[UserSelectResponse] = Field(
        description="List of users matching the query.",
    )

    users_count: int = Field(
        ge=0,
        description="Total number of users matching the query.",
    )
