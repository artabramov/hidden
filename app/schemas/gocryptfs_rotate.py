# app/schemas/gocryptfs_rotate.py
# SPDX-License-Identifier: Apache-2.0

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.pydantic.master_password import (
    MASTER_PASSWORD_AUTH_DESCRIPTION,
    MASTER_PASSWORD_SET_DESCRIPTION,
    validate_master_password,
)


class GocryptfsRotateRequest(BaseModel):
    """
    Request schema for changing the master password.

    Composition validation applies only to the new password, not the
    current one used for authentication.
    """

    model_config = ConfigDict(
        extra="forbid",
    )

    current_master_password: str = Field(
        description=MASTER_PASSWORD_AUTH_DESCRIPTION,
    )

    changed_master_password: str = Field(
        min_length=16,
        max_length=1024,
        description=MASTER_PASSWORD_SET_DESCRIPTION,
    )

    @field_validator("changed_master_password")
    @classmethod
    def validate_changed_master_password(cls, value: str) -> str:
        return validate_master_password(value)
