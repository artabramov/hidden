# app/routers/audit_list.py
# SPDX-License-Identifier: GPL-3.0-only

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.auth import AccessLevel, require_access
from app.dependencies.session import get_session
from app.models.user import User
from app.schemas.audit_list import (
    AUDIT_LIST_ERRORS,
    AuditListRequest,
    AuditListResponse,
)
from app.services.audit_list import list_audit

router = APIRouter(tags=["Services"])


@router.get(
    "/audit",
    response_model=AuditListResponse,
    responses=AUDIT_LIST_ERRORS,
    status_code=status.HTTP_200_OK,
    summary="List audit records (filtered, paginated)",
)
async def audit_list_router(
    session: AsyncSession = Depends(get_session),
    params: AuditListRequest = Depends(),
    current_user: User = Depends(require_access(AccessLevel.ADMIN)),
) -> AuditListResponse:
    """
    Returns a filtered list of audit records with pagination and
    ordering. It allows an administrator to retrieve audit records
    that match the provided query parameters.

    **Hooks:**

    `AUDIT_LIST_COMPLETED` — executed after the audit list is retrieved.

    **Authentication:**

    - Requires a valid token with admin access.

    **Request query:**

    `AuditListRequest` — pagination, ordering, and optional filters.

    **Response:**

    `AuditListResponse` — current page of audit records and total
    count of audit records matching the filters (before pagination).

    **Response codes:**

    - `200` — Audit list returned successfully.
    - `401` — Invalid, expired, or missing token.
    - `403` — User not admin, inactive, or blocked.
    - `422` — Input values failed validation.
    - `503` — Service temporarily unavailable.
    """
    audit, audit_count = await list_audit(
        session=session,
        params=params,
    )
    return AuditListResponse(audit=audit, audit_count=audit_count)
