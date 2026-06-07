# app/schemas/variable_get.py
# SPDX-License-Identifier: SSPL-1.0

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.pydantic_error import PydanticErrorResponse

VARIABLE_GET_ERRORS = {
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
        "description": "Variable was not found.",
    },
    422: {
        "model": PydanticErrorResponse,
        "description": (
            "Input values failed validation (invalid namespace or "
            "variable key format or length)."
        ),
    },
    503: {
        "description": (
            "Service is temporarily unavailable (lockdown mode enabled "
            "or gocryptfs storage not ready)."
        ),
    },
}


class VariableGetResponse(BaseModel):
    """
    Response schema for selecting a variable by namespace and key.
    """

    model_config = ConfigDict(
        extra="forbid",
        from_attributes=True,
        populate_by_name=True,
    )

    created_at: int = Field(
        description="Timestamp when the variable was created.",
    )

    updated_at: int | None = Field(
        default=None,
        description="Timestamp of the last variable update.",
    )

    created_by: int = Field(
        description="Identifier of the user who created the variable.",
    )

    updated_by: int | None = Field(
        default=None,
        description="Identifier of the user who last updated the variable.",
    )

    namespace: str = Field(
        description="Logical namespace of the variable.",
    )

    variable_key: str = Field(
        description="Unique variable name within the namespace.",
    )

    variable_value: str = Field(
        description="Stored value of the variable.",
    )
