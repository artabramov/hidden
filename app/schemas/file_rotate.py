# app/schemas/file_rotate.py
# SPDX-License-Identifier: SSPL-1.0

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.pydantic_error import PydanticErrorResponse

FILE_ROTATE_ERRORS = {
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
            "File is not an image, image format is unsupported, "
            "or filesystem state conflicts with the database."
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


class FileRotateRequest(BaseModel):
    """
    Request schema for rotating an image file. A successful rotation
    creates a new file revision.
    """

    model_config = ConfigDict(
        extra="forbid",
    )

    angle: Literal[90, 180, 270] = Field(
        description="Clockwise rotation angle in degrees.",
    )


class FileRotateResponse(BaseModel):
    """
    Response schema for image rotation.
    """

    model_config = ConfigDict(
        extra="forbid",
        from_attributes=True,
        populate_by_name=True,
    )

    file_id: int = Field(
        validation_alias="id",
        description="Identifier of the rotated file.",
    )
