# app/schemas/audit_select.py
# SPDX-License-Identifier: GPL-3.0-only

from pydantic import BaseModel, ConfigDict, Field


class AuditSelectResponse(BaseModel):
    """
    Response schema for a single audit record containing audit event
    metadata, actor reference, request reference, and target resource
    reference.
    """

    model_config = ConfigDict(
        extra="forbid",
        from_attributes=True,
        populate_by_name=True,
    )

    audit_id: int = Field(
        validation_alias="id",
        description="Identifier of the audit record.",
    )

    created_at: int = Field(
        description="Timestamp when the audit record was created.",
    )

    created_by: int | None = Field(
        default=None,
        description="Identifier of the user who created the audit record.",
    )

    event: str = Field(
        description="Audit event name.",
    )

    request_uuid: str | None = Field(
        default=None,
        description="Request UUID associated with the audit record.",
    )

    resource_type: str | None = Field(
        default=None,
        description="Type of resource associated with the audit record.",
    )

    resource_id: int | None = Field(
        default=None,
        description="Identifier of the resource associated with the record.",
    )
