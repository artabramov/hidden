# app/models/audit.py
# SPDX-License-Identifier: SSPL-1.0

import time

from sqlalchemy import ForeignKey, Integer, String, event
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Audit(Base):
    __tablename__ = "audit"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    created_at: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=lambda: int(time.time()),
        index=True,
    )

    created_by: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )

    event: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
        index=True,
    )

    request_uuid: Mapped[str | None] = mapped_column(
        String(64),
        nullable=True,
        index=True,
    )

    resource_type: Mapped[str | None] = mapped_column(
        String(64),
        nullable=True,
        index=True,
    )

    resource_id: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        index=True,
    )

    __table_args__ = (
        {"sqlite_autoincrement": True},
    )


# NOTE (ADR-24): Audit data is append-only.
# UPDATE and DELETE operations must fail when performed through the
# ORM. This protection is application-level only. It does not prevent
# mutations via raw SQL or direct database access.

@event.listens_for(Audit, "before_update", propagate=True)
def prevent_update(mapper, connection, target):
    raise RuntimeError("Audit records cannot be updated")


@event.listens_for(Audit, "before_delete", propagate=True)
def prevent_delete(mapper, connection, target):
    raise RuntimeError("Audit records cannot be deleted")
