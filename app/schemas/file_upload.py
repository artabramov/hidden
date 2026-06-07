# app/schemas/file_upload.py
# SPDX-License-Identifier: SSPL-1.0

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.pydantic_error import PydanticErrorResponse

FILE_UPLOAD_ERRORS = {
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
        "description": "Target folder was not found.",
    },
    409: {
        "description": (
            "Target filename conflicts with a directory, an unmanaged "
            "filesystem file, a path-length limit, or an existing file "
            "with incompatible MIME type."
        ),
    },
    422: {
        "model": PydanticErrorResponse,
        "description": (
            "Invalid input (missing file or invalid filename)."
        ),
    },
    423: {
        "description": "Target folder is write-protected.",
    },
    503: {
        "description": (
            "Service is temporarily unavailable (lockdown mode enabled "
            "or gocryptfs storage not ready)."
        ),
    },
}


class FileUploadResponse(BaseModel):
    """
    Response schema for file upload containing the created file
    identifier.
    """

    model_config = ConfigDict(
        extra="forbid",
        from_attributes=True,
    )

    file_id: int = Field(
        validation_alias="id",
        description="Identifier of the uploaded file.",
    )
