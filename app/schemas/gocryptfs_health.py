# app/schemas/gocryptfs_health.py
# SPDX-License-Identifier: Apache-2.0

from pydantic import BaseModel, ConfigDict, Field


class GocryptfsHealthResponse(BaseModel):
    """
    Response schema for the gocryptfs runtime health snapshot.
    """

    model_config = ConfigDict(
        extra="forbid",
    )

    is_cipherdir_created: bool = Field(
        description="Whether the gocryptfs cipherdir appears initialized.",
    )
    is_cipherdir_mounted: bool = Field(
        description="Whether the gocryptfs mountpoint is currently mounted.",
    )
    is_versity_created: bool = Field(
        description="Whether the VersityGW credentials have been created.",
    )
    is_versity_running: bool = Field(
        description="Whether the VersityGW process is currently running.",
    )
    is_watchdog_alive: bool = Field(
        description=(
            "Whether the watchdog heartbeat is fresh within "
            "WATCHDOG_LIVENESS_SECONDS."
        ),
    )
    unix_timestamp: int = Field(
        description=(
            "Current instant as Unix time (seconds since 1970-01-01 UTC)."
        ),
    )
    timezone_name: str = Field(
        description="Host local timezone name (IANA, tzname, or fallback).",
    )
