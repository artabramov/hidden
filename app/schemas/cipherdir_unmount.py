# app/schemas/cipherdir_unmount.py
# SPDX-License-Identifier: SSPL-1.0

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.pydantic_error import PydanticErrorResponse

CIPHERDIR_UNMOUNT_ERRORS = {
    404: {
        "description": (
            "Cipherdir is not initialized or encrypted passphrase file "
            "is missing (empty response body)."
        ),
    },
    409: {
        "description": (
            "Cipherdir is not mounted."
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


class CipherdirUnmountRequest(BaseModel):
    """
    Request schema for unmounting the storage mountpoint requiring
    the master password for authorization.
    """

    model_config = ConfigDict(
        extra="forbid",
    )

    master_password: str = Field(
        description="Master password used to unmount the cipherdir.",
    )
