# app/schemas/folder_delete.py
# SPDX-License-Identifier: SSPL-1.0

from app.schemas.pydantic_error import PydanticErrorResponse

FOLDER_DELETE_ERRORS = {
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
            "Folder cannot be deleted because it contains subfolders "
            "or still has files after deletion attempt."
        ),
    },
    422: {
        "model": PydanticErrorResponse,
        "description": (
            "Input values failed validation (invalid folder ID)."
        ),
    },
    423: {
        "description": "Target folder or parent folder is write-protected.",
    },
    503: {
        "description": (
            "Service is temporarily unavailable (lockdown mode enabled "
            "or gocryptfs storage not ready)."
        ),
    },
}
