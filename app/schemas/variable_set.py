# app/schemas/variable_set.py
# SPDX-License-Identifier: GPL-3.0-only

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.pydantic_error import PydanticErrorResponse

VARIABLE_SET_ERRORS = {
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
        "model": PydanticErrorResponse,
        "description": (
            "Input values failed validation (invalid namespace or key "
            "format or length, or variable value conflicts with "
            "existing data)."
        ),
    },
    503: {
        "description": (
            "Service is temporarily unavailable (lockdown mode enabled "
            "or gocryptfs storage not ready)."
        ),
    },
}


class VariableSetRequest(BaseModel):
    """
    Request body for setting a variable value. Leading and trailing
    whitespace is stripped on the value field.
    """

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )

    variable_value: str = Field(
        description=(
            "Serialized value to persist for the namespace and key."
        ),
    )
