# app/schemas/file_move.py
# SPDX-License-Identifier: SSPL-1.0

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.pydantic_error import PydanticErrorResponse

FILE_MOVE_ERRORS = {
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
        "description": "Target file or destination folder was not found.",
    },
    409: {
        "description": (
            "A file with the same filename already exists in the "
            "destination folder, or the destination filesystem path "
            "conflicts with an existing directory or unmanaged file."
        ),
    },
    422: {
        "model": PydanticErrorResponse,
        "description": (
            "Input values failed validation (invalid file ID or "
            "invalid destination folder ID)."
        ),
    },
    423: {
        "description": (
            "Source or destination folder is write-protected."
        ),
    },
    503: {
        "description": (
            "Service is temporarily unavailable (lockdown mode enabled "
            "or gocryptfs storage not ready)."
        ),
    },
}


class FileMoveRequest(BaseModel):
    """
    Request schema for moving a file to another folder.
    """

    model_config = ConfigDict(
        extra="forbid",
    )

    folder_id: int = Field(
        ge=1,
        description="Identifier of the destination folder.",
    )


class FileMoveResponse(BaseModel):
    """
    Response schema for file move containing the moved file identifier
    and its destination folder identifier.
    """

    model_config = ConfigDict(
        extra="forbid",
        from_attributes=True,
        populate_by_name=True,
    )

    file_id: int = Field(
        validation_alias="id",
        description="Identifier of the moved file.",
    )

    folder_id: int = Field(
        description="Identifier of the destination folder.",
    )
