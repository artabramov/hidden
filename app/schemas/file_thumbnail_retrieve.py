# app/schames/file_thumbnail_retrieve.py
# SPDX-License-Identifier: GPL-3.0-only

FILE_THUMBNAIL_RETRIEVE_ERRORS = {
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
        "description": "File thumbnail was not found.",
    },
    422: {
        "description": "Input values failed validation.",
    },
    503: {
        "description": (
            "Service is temporarily unavailable (lockdown mode enabled "
            "or gocryptfs storage not ready)."
        ),
    },
}
