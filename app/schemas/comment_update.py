# app/schemas/comment_update.py
# SPDX-License-Identifier: SSPL-1.0

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.pydantic_error import PydanticErrorResponse

COMMENT_UPDATE_ERRORS = {
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
        "description": "Target comment was not found.",
    },
    422: {
        "model": PydanticErrorResponse,
        "description": (
            "Input values failed validation (invalid comment ID, missing "
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


class CommentUpdateRequest(BaseModel):
    """
    Request schema for updating a file comment. Leading and trailing
    whitespace is stripped from the comment body.
    """

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )

    body: str = Field(
        min_length=1,
        max_length=4096,
        description="Updated comment body.",
    )


class CommentUpdateResponse(BaseModel):
    """
    Response schema for file comment update containing the updated
    comment identifier.
    """

    model_config = ConfigDict(
        extra="forbid",
        from_attributes=True,
    )

    comment_id: int = Field(
        validation_alias="id",
        description="Identifier of the updated comment.",
    )
