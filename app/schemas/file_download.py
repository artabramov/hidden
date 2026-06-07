# app/schemas/file_download.py
# SPDX-License-Identifier: SSPL-1.0

from app.schemas.pydantic_error import PydanticErrorResponse

FILE_DOWNLOAD_ERRORS = {
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
        "description": "File was not found.",
    },
    422: {
        "model": PydanticErrorResponse,
        "description": (
            "Input values failed validation (e.g. non-integer file ID "
            "in the path)."
        ),
    },
    503: {
        "description": (
            "Service is temporarily unavailable (lockdown mode enabled "
            "or gocryptfs storage not ready)."
        ),
    },
}
