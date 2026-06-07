# app/schemas/variable_list.py
# SPDX-License-Identifier: SSPL-1.0


VARIABLE_LIST_ERRORS = {
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
    422: {
        "description": (
            "Input values failed validation (invalid namespace format "
            "or length)."
        ),
    },
    503: {
        "description": (
            "Service is temporarily unavailable (lockdown mode enabled "
            "or gocryptfs storage not ready)."
        ),
    },
}
