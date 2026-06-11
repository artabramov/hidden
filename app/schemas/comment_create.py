# app/schemas/comment_create.py
# SPDX-License-Identifier: GPL-3.0-only

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.pydantic_error import PydanticErrorResponse

COMMENT_CREATE_ERRORS = {
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
        "description": "Target file was not found.",
    },
    422: {
        "model": PydanticErrorResponse,
        "description": (
            "Input values failed validation (invalid file ID, missing "
            "body, empty body, or body too long)."
        ),
    },
    423: {
        "description": "Parent folder is write-protected.",
    },
    503: {
        "description": (
            "Service is temporarily unavailable (lockdown mode enabled "
            "or gocryptfs storage not ready)."
        ),
    },
}


class CommentCreateRequest(BaseModel):
    """
    Request schema for creating a file comment. Leading and trailing
    whitespace is stripped from the comment body.
    """

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )

    body: str = Field(
        min_length=1,
        max_length=4096,
        description="Comment body.",
    )


class CommentCreateResponse(BaseModel):
    """
    Response schema for file comment creation containing the created
    comment identifier.
    """

    model_config = ConfigDict(
        extra="forbid",
        from_attributes=True,
    )

    comment_id: int = Field(
        validation_alias="id",
        description="Identifier of the created comment.",
    )
