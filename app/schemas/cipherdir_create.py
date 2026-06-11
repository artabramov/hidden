# app/schemas/cipherdir_create.py
# SPDX-License-Identifier: GPL-3.0-only

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.constants import MASTER_PASSWORD_MIN_LENGTH
from app.schemas.pydantic_error import PydanticErrorResponse
from app.validators.master_password import validate_master_password

CIPHERDIR_CREATE_ERRORS = {
    409: {
        "description": (
            "Cipherdir is already initialized or required secret files "
            "already exist (gocryptfs passphrase, JWT signing key, or "
            "Fernet key)."
        ),
    },
    422: {
        "model": PydanticErrorResponse,
        "description": (
            "Input values failed validation (missing master password or "
            "invalid master password length or strength)."
        ),
    },
}


class CipherdirCreateRequest(BaseModel):
    """
    Request schema for creating the encrypted storage requiring
    a master password with validation of strength and length.
    """

    model_config = ConfigDict(
        extra="forbid",
    )

    master_password: str = Field(
        min_length=MASTER_PASSWORD_MIN_LENGTH,
        max_length=1024,
        description="Master password used to initialize the cipherdir.",
    )

    @field_validator("master_password")
    @classmethod
    def validate_master_password_field(cls, value: str) -> str:
        return validate_master_password(value)
