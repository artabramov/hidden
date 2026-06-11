# app/models/variable.py
# SPDX-License-Identifier: GPL-3.0-only

import time

from sqlalchemy import (
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

# NOTE (ADR-66): Variable table stores application key-value data.
# It is used for extensions and infrastructure-level configuration
# persisted in the database.

# NOTE (ADR-67): Variable keys are namespaced.
# Namespacing avoids collisions between extensions.
# Example: namespace="pics", variable_key="width", variable_value="320".


class Variable(Base):
    __tablename__ = "variables"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    namespace: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
    )

    variable_key: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    variable_value: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    created_by: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )

    updated_by: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )

    created_at: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=lambda: int(time.time()),
        index=True,
    )

    updated_at: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        onupdate=lambda: int(time.time()),
    )

    variable_created_by_user: Mapped["User | None"] = relationship(  # noqa: E501, F821
        "User",
        foreign_keys=[created_by],
        lazy="selectin",
    )

    variable_updated_by_user: Mapped["User | None"] = relationship(  # noqa: E501, F821
        "User",
        foreign_keys=[updated_by],
        lazy="selectin",
    )

    __table_args__ = (
        Index(
            "uq_variables_namespace_variable_key",
            "namespace",
            "variable_key",
            unique=True,
        ),
        {"sqlite_autoincrement": True},
    )
