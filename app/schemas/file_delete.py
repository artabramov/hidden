# app/schemas/file_delete.py
# SPDX-License-Identifier: GPL-3.0-only

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.pydantic_error import PydanticErrorResponse

FILE_DELETE_ERRORS = {
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
        "description": "Input values failed validation (invalid file ID).",
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


class FileDeleteResponse(BaseModel):
    """
    Response schema for file deletion containing the deleted file
    identifier.
    """

    model_config = ConfigDict(
        extra="forbid",
        from_attributes=True,
    )

    file_id: int = Field(
        validation_alias="id",
        description="Identifier of the deleted file.",
    )
