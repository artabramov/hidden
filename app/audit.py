# app/audit.py
# SPDX-License-Identifier: GPL-3.0-only

from app.context import get_context_var
from app.models.audit import Audit
from app.repositories.orm import ORMRepository

# NOTE (ADR-21): Commit ownership and transaction boundaries.
# The service layer owns transaction boundaries at the core application
# level and is responsible for explicit commit and rollback of the
# session.

# NOTE (ADR-22): Commit behavior of lower-level components.
# Audit and ORM repository support autonomous commit for universality
# (e.g., extensions or isolated usage), but within the core application
# they must only append changes to the current session and must not
# control transaction boundaries.

# NOTE (ADR-69): Low-level services without audit rows.
# Cipherdir create/mount/unmount, master password change, and lockdown
# enable/disable do not call audit. They must remain usable without an
# application AsyncSession or an open SQLite file (cipherdir may be
# unmounted; SQLite lives on the mount).


async def write_audit(
    repository: ORMRepository,
    event: str,
    current_user_id: int | None = None,
    resource_type: str | None = None,
    resource_id: int | None = None,
    commit: bool = False,
) -> None:
    """
    Persist an audit event in the current transaction. Current user
    and request correlation are resolved from request context.
    """
    if current_user_id is None:
        current_user_id = get_context_var("current_user_id")

    audit_event = Audit(
        created_by=current_user_id,
        event=event,
        request_uuid=get_context_var("request_uuid"),
        resource_type=resource_type,
        resource_id=resource_id,
    )

    await repository.insert(audit_event, commit=commit)
