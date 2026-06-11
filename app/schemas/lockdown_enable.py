# app/schemas/lockdown_enable.py
# SPDX-License-Identifier: GPL-3.0-only

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.pydantic_error import PydanticErrorResponse

LOCKDOWN_ENABLE_ERRORS = {
    404: {
        "description": (
            "Encrypted gocryptfs passphrase file was not found."
        ),
    },
    409: {
        "description": (
            "Lockdown mode is already enabled."
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


class LockdownEnableRequest(BaseModel):
    """
    Request schema for enabling lockdown mode requiring the master
    password for authorization.
    """

    model_config = ConfigDict(
        extra="forbid",
    )

    master_password: str = Field(
        description="Master password used to enable lockdown mode.",
    )
