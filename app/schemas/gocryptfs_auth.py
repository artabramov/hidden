# app/schemas/gocryptfs_auth.py
# SPDX-License-Identifier: Apache-2.0

from pydantic import BaseModel, ConfigDict, Field

from app.pydantic.master_password import MASTER_PASSWORD_AUTH_DESCRIPTION


class GocryptfsAuthRequest(BaseModel):
    """
    Request body for gocryptfs operations that authenticate with the
    stored master password.

    Composition is not validated; correctness is verified by decrypting
    the stored passphrase.
    """

    model_config = ConfigDict(
        extra="forbid",
    )

    master_password: str = Field(
        description=MASTER_PASSWORD_AUTH_DESCRIPTION,
    )
