# app/schemas/file_starred_change.py
# SPDX-License-Identifier: SSPL-1.0

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.pydantic_error import PydanticErrorResponse

FILE_STARRED_ERRORS = {
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
            "Input values failed validation (invalid file ID, "
            "missing required fields, invalid starred value, "
            "or extra fields)."
        ),
    },
    503: {
        "description": (
            "Service is temporarily unavailable (lockdown mode enabled "
            "or gocryptfs storage not ready)."
        ),
    },
}


class FileStarredChangeRequest(BaseModel):
    """
    Request schema for changing a file's starred flag.
    """

    model_config = ConfigDict(
        extra="forbid",
    )

    is_starred: bool = Field(
        description="Whether the target file is starred.",
    )


class FileStarredChangeResponse(BaseModel):
    """
    Response schema for file starred flag update.
    """

    model_config = ConfigDict(
        extra="forbid",
        from_attributes=True,
        populate_by_name=True,
    )

    file_id: int = Field(
        validation_alias="id",
        description="Identifier of the updated file.",
    )
