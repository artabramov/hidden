# app/schemas/cipherdir_mount.py
# SPDX-License-Identifier: SSPL-1.0

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.pydantic_error import PydanticErrorResponse

CIPHERDIR_MOUNT_ERRORS = {
    404: {
        "description": (
            "Cipherdir is not initialized or encrypted passphrase file "
            "is missing."
        ),
    },
    409: {
        "description": (
            "Cipherdir is already mounted."
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


class CipherdirMountRequest(BaseModel):
    """
    Request schema for mounting the storage mountpoint requiring
    the master password for decryption.
    """

    model_config = ConfigDict(
        extra="forbid",
    )

    master_password: str = Field(
        description="Master password used to mount the cipherdir.",
    )
