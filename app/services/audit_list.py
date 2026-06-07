# app/services/audit_list.py
# SPDX-License-Identifier: SSPL-1.0

import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.events import Events as E
from app.hooks import hooks
from app.models.audit import Audit
from app.repositories.orm import ORMRepository
from app.schemas.audit_list import AuditListRequest

log = logging.getLogger(__name__)


async def list_audit(
    session: AsyncSession,
    params: AuditListRequest,
) -> tuple[list[Audit], int]:
    """
    Return audit records matching the provided filters together with
    the total number of matching records.
    """
    log.info("event=%s", E.AUDIT_LIST_STARTED)

    repository = ORMRepository(session)
    filters = params.model_dump(exclude_none=True)

    if "event__ilike" in filters:
        filters["event__ilike"] = f"%{filters['event__ilike']}%"

    audit_count = await repository.count_all(Audit, **filters)
    audit = await repository.select_all(Audit, **filters)

    log.info("event=%s", E.AUDIT_LIST_COMPLETED)
    await hooks.emit(E.AUDIT_LIST_COMPLETED, session, audit)
    return audit, audit_count
