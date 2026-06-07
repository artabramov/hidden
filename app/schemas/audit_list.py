# app/schemas/audit_list.py
# SPDX-License-Identifier: SSPL-1.0

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.audit_select import AuditSelectResponse
from app.schemas.pydantic_error import PydanticErrorResponse

OrderByField = Literal[
    "id",
    "created_at",
    "created_by",
    "event",
    "request_uuid",
    "resource_type",
    "resource_id",
]


AUDIT_LIST_ERRORS = {
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
            "invalid ordering values, or invalid offset / limit)."
        ),
    },
    503: {
        "description": (
            "Service is temporarily unavailable (lockdown mode enabled "
            "or gocryptfs storage not ready)."
        ),
    },
}


class AuditListRequest(BaseModel):
    """
    Request schema for querying audit records with filtering by
    timestamps, actor, event, request UUID, and resource, as well as
    pagination and ordering. Extra fields are forbidden. Leading and
    trailing whitespace is stripped from string fields.
    """

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )

    created_at__ge: int | None = Field(
        default=None,
        ge=0,
        description="Lower bound for audit creation timestamp.",
    )

    created_at__le: int | None = Field(
        default=None,
        ge=0,
        description="Upper bound for audit creation timestamp.",
    )

    created_by__eq: int | None = Field(
        default=None,
        ge=1,
        description="Filter by creator user ID.",
    )

    event__ilike: str | None = Field(
        default=None,
        description="Case-insensitive substring match for event name.",
    )

    request_uuid__eq: str | None = Field(
        default=None,
        description="Filter by request UUID.",
    )

    resource_type__eq: str | None = Field(
        default=None,
        description="Filter by resource type.",
    )

    resource_id__eq: int | None = Field(
        default=None,
        ge=1,
        description="Filter by resource ID.",
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
        default="created_at",
        description="Field used for result ordering.",
    )

    order: Literal["asc", "desc"] = Field(
        default="desc",
        description="Ordering direction.",
    )


class AuditListResponse(BaseModel):
    """
    Response schema for audit listing containing matched audit records
    and the total number of audit records satisfying the query
    conditions.
    """

    model_config = ConfigDict(
        extra="forbid",
    )

    audit: list[AuditSelectResponse] = Field(
        description="List of audit records matching the query.",
    )
    audit_count: int = Field(
        ge=0,
        description="Total number of audit records matching the query.",
    )
