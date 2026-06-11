# app/schemas/file_tag_list.py
# SPDX-License-Identifier: GPL-3.0-only

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.pydantic_error import PydanticErrorResponse


TAG_LIST_ERRORS = {
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
    422: {
        "model": PydanticErrorResponse,
        "description": (
            "Input values failed validation (invalid limit value)."
        ),
    },
    503: {
        "description": (
            "Service is temporarily unavailable (lockdown mode enabled "
            "or gocryptfs storage not ready)."
        ),
    },
}


class TagListRequest(BaseModel):
    """
    Request schema for listing the most frequently used tags.
    Extra fields are forbidden.
    """

    model_config = ConfigDict(extra="forbid")

    limit: int = Field(
        default=50,
        ge=1,
        le=1000,
        description="Maximum number of tags to return.",
    )


class TagListItemResponse(BaseModel):
    """
    Response schema for one tag item in tag listing.
    """

    model_config = ConfigDict(extra="forbid")

    tag: str = Field(
        description="Tag name.",
    )

    usage_count: int = Field(
        ge=0,
        description="Number of files that use this tag.",
    )
