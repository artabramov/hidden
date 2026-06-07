# app/schemas/folder_write_protect.py
# SPDX-License-Identifier: SSPL-1.0

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.pydantic_error import PydanticErrorResponse

FOLDER_WRITE_PROTECT_ERRORS = {
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
    422: {
        "model": PydanticErrorResponse,
        "description": (
            "Input values failed validation (invalid folder ID, "
            "missing required fields, invalid write-protected value, "
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


class FolderWriteProtectRequest(BaseModel):
    """
    Request schema for changing a folder's explicit write-protection
    flag.
    """

    model_config = ConfigDict(
        extra="forbid",
    )

    is_write_protected: bool = Field(
        description=(
            "Whether the target folder is explicitly write-protected."
        ),
    )
