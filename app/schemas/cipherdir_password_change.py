# app/schemas/cipherdir_password_change.py
# SPDX-License-Identifier: GPL-3.0-only

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.constants import MASTER_PASSWORD_MIN_LENGTH
from app.schemas.pydantic_error import PydanticErrorResponse
from app.validators.master_password import validate_master_password

CIPHERDIR_PASSWORD_CHANGE_ERRORS = {
    404: {
        "description": (
            "Cipherdir is not initialized or encrypted passphrase file "
            "is missing."
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
            "Input values failed validation (missing required fields, "
            "invalid current master password, passphrase decryption "
            "failed, or invalid new master password length or strength)."
        ),
    },
}


class CipherdirPasswordChangeRequest(BaseModel):
    """
    Request schema for changing the encrypted storage master password
    with validation of the new password strength and length.
    """

    model_config = ConfigDict(
        extra="forbid",
    )

    current_master_password: str = Field(
        description="Current master password used for authentication.",
    )

    changed_master_password: str = Field(
        min_length=MASTER_PASSWORD_MIN_LENGTH,
        max_length=1024,
        description="New master password to replace the current one.",
    )

    @field_validator("changed_master_password")
    @classmethod
    def validate_changed_master_password(cls, value: str) -> str:
        return validate_master_password(value)
