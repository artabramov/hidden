# app/schemas/file_flip.py
# SPDX-License-Identifier: SSPL-1.0

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.pydantic_error import PydanticErrorResponse

FILE_FLIP_ERRORS = {
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


class FileFlipRequest(BaseModel):
    """
    Request schema for flipping an image file. A successful flip creates
    a new file revision.
    """

    model_config = ConfigDict(
        extra="forbid",
    )

    axis: Literal["horizontal", "vertical"] = Field(
        description="Flip axis: horizontal or vertical.",
    )


class FileFlipResponse(BaseModel):
    """
    Response schema for image flip.
    """

    model_config = ConfigDict(
        extra="forbid",
        from_attributes=True,
        populate_by_name=True,
    )

    file_id: int = Field(
        validation_alias="id",
        description="Identifier of the flipped file.",
    )
