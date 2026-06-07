# app/schemas/file_edit.py
# SPDX-License-Identifier: SSPL-1.0

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.pydantic_error import PydanticErrorResponse

FILE_EDIT_ERRORS = {
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
    409: {
        "description": (
            "File is not a text file or filesystem state conflicts "
            "with the database."
        ),
    },
    422: {
        "model": PydanticErrorResponse,
        "description": (
            "Input values failed validation."
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


class FileEditRequest(BaseModel):
    """
    Request schema for editing a text file. A successful edit creates
    a new file revision.
    """

    model_config = ConfigDict(
        extra="forbid",
    )

    content: str = Field(
        description="New text file content.",
    )


class FileEditResponse(BaseModel):
    """
    Response schema for text file edit.
    """

    model_config = ConfigDict(
        extra="forbid",
        from_attributes=True,
        populate_by_name=True,
    )

    file_id: int = Field(
        validation_alias="id",
        description="Identifier of the edited file.",
    )
