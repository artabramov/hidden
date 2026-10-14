# app/schemas/gocryptfs_reveal.py
# SPDX-License-Identifier: Apache-2.0

from pydantic import BaseModel, ConfigDict, Field


class GocryptfsRevealResponse(BaseModel):
    """
    Response schema containing the decrypted gocryptfs passphrase
    and VersityGW root credentials.
    """

    model_config = ConfigDict(
        extra="forbid",
    )

    gocryptfs_passphrase: str = Field(
        description="Decrypted gocryptfs passphrase.",
    )

    versity_access_key: str = Field(
        description="VersityGW root access key.",
    )

    versity_secret_key: str = Field(
        description="VersityGW root secret key.",
    )
