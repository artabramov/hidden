# app/schemas/gocryptfs_init.py
# SPDX-License-Identifier: Apache-2.0

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.pydantic.master_password import (
    MASTER_PASSWORD_SET_DESCRIPTION,
    validate_master_password,
)


class GocryptfsInitRequest(BaseModel):
    """
    Request schema for creating encrypted storage.

    Sets the master password and applies composition validation.
    """

    model_config = ConfigDict(
        extra="forbid",
    )

    master_password: str = Field(
        min_length=16,
        max_length=1024,
        description=MASTER_PASSWORD_SET_DESCRIPTION,
    )

    @field_validator("master_password")
    @classmethod
    def validate_master_password_field(cls, value: str) -> str:
        return validate_master_password(value)


class GocryptfsInitResponse(BaseModel):
    """
    Response schema containing the generated VersityGW root
    credentials.
    """

    model_config = ConfigDict(
        extra="forbid",
    )

    access_key: str = Field(
        description="VersityGW root access key.",
    )

    secret_key: str = Field(
        description="VersityGW root secret key.",
    )
