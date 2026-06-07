# app/models/file_comment.py
# SPDX-License-Identifier: SSPL-1.0

import time

from sqlalchemy import (
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

# NOTE (ADR-65): Only the creator can modify a file comment.
# Only the user who created the comment (created_by) may update or
# delete it. This restriction applies regardless of RBAC role.


class FileComment(Base):
    __tablename__ = "files_comments"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    file_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("files.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    created_by: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
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

    body: Mapped[str] = mapped_column(
        String(4096),
        nullable=False,
    )

    comment_file: Mapped["File"] = relationship(  # noqa: F821
        "File",
        back_populates="file_comments",
        lazy="selectin",
        passive_deletes=True,
    )

    comment_created_by_user: Mapped["User"] = relationship(  # noqa: F821
        "User",
        foreign_keys=[created_by],
        lazy="selectin",
    )

    __table_args__ = (
        {"sqlite_autoincrement": True},
    )
