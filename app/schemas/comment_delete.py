# app/schemas/comment_delete.py
# SPDX-License-Identifier: GPL-3.0-only

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.pydantic_error import PydanticErrorResponse

COMMENT_DELETE_ERRORS = {
    401: {
        "description": (
            "Invalid, expired, or missing authentication token."
        ),
    },
    403: {
        "description": (
            "Authenticated user is inactive, blocked, lacks required "
            "permissions, or is not the comment creator."
        ),
    },
    404: {
        "description": "Target comment was not found.",
    },
    422: {
        "model": PydanticErrorResponse,
        "description": "Input values failed validation (invalid comment ID).",
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


class CommentDeleteResponse(BaseModel):
    """
    Response schema for file comment deletion containing the deleted
    comment identifier.
    """

    model_config = ConfigDict(
        extra="forbid",
        from_attributes=True,
    )

    comment_id: int = Field(
        validation_alias="id",
        description="Identifier of the deleted comment.",
    )
