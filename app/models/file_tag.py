# app/models/file_tag.py
# SPDX-License-Identifier: SSPL-1.0

import time

from sqlalchemy import (
    ForeignKey,
    Index,
    Integer,
    String,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class FileTag(Base):
    __tablename__ = "files_tags"

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

    tag: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
    )

    tag_file: Mapped["File"] = relationship(  # noqa: F821
        "File",
        back_populates="file_tags",
        lazy="selectin",
        passive_deletes=True,
    )

    tag_created_by_user: Mapped["User"] = relationship(  # noqa: F821
        "User",
        foreign_keys=[created_by],
        lazy="selectin",
    )

    __table_args__ = (
        Index(
            "uq_files_tags_file_id_tag",
            "file_id",
            func.lower(tag),
            unique=True,
        ),
        {"sqlite_autoincrement": True},
    )
