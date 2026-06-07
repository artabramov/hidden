# app/schemas/lockdown_disable.py
# SPDX-License-Identifier: SSPL-1.0

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.pydantic_error import PydanticErrorResponse

LOCKDOWN_DISABLE_ERRORS = {
    404: {
        "description": (
            "Encrypted gocryptfs passphrase file was not found."
        ),
    },
    409: {
        "description": (
            "Lockdown mode is already disabled."
        ),
    },
    429: {
        "description": (
            "Master password verification attempts are throttled "
            "(minimum interval between attempts in this process)."
        ),
    },
    422: {
        "model": PydanticErrorResponse,
        "description": (
            "Input values failed validation (invalid master password "
            "or passphrase decryption failed)."
        ),
    },
}


class LockdownDisableRequest(BaseModel):
    """
    Request schema for disabling lockdown mode requiring the master
    password for authorization.
    """

    model_config = ConfigDict(
        extra="forbid",
    )

    master_password: str = Field(
        description="Master password used to disable lockdown mode.",
    )
