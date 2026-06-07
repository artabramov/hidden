# app/schemas/folder_list.py
# SPDX-License-Identifier: SSPL-1.0

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.folder_select import FolderSelectResponse
from app.schemas.pydantic_error import PydanticErrorResponse

OrderByField = Literal[
    "id",
    "created_at",
    "updated_at",
    "dirname",
    "is_write_protected",
]


FOLDER_LIST_ERRORS = {
    401: {
        "description": (
            "Invalid, expired, or missing authentication token."
        ),
    },
    403: {
        "description": (
            "Authenticated user is inactive, blocked, or lacks "
            "required permissions."
        ),
    },
    404: {
        "description": "Parent folder was not found.",
    },
    422: {
        "model": PydanticErrorResponse,
        "description": (
            "Input values failed validation (invalid parent folder filter "
            "or ordering values)."
        ),
    },
    503: {
        "description": (
            "Service is temporarily unavailable (lockdown mode enabled "
            "or gocryptfs storage not ready)."
        ),
    },
}


class FolderListRequest(BaseModel):
    """
    Request schema for querying direct child folders with optional
    parent filter and ordering. Extra fields are forbidden.
    """

    model_config = ConfigDict(
        extra="forbid",
    )

    parent_id__eq: int | None = Field(
        default=None,
        ge=1,
        description=(
            "When omitted or null, list folders at the hierarchy root. "
            "When set, list direct children of the folder with this "
            "identifier."
        ),
    )

    order_by: OrderByField = Field(
        default="dirname",
        description="Field used for result ordering.",
    )

    order: Literal["asc", "desc"] = Field(
        default="asc",
        description="Ordering direction.",
    )


class FolderListResponse(BaseModel):
    """
    Response schema for folder listing containing matched direct child
    folders and the total number of folders satisfying the query
    conditions.
    """

    model_config = ConfigDict(
        extra="forbid",
    )

    folders: list[FolderSelectResponse] = Field(
        description="List of direct child folders matching the query.",
    )

    folders_count: int = Field(
        ge=0,
        description="Total number of folders matching the query.",
    )
