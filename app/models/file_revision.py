# app/models/file_revision.py
# SPDX-License-Identifier: SSPL-1.0

import os
import time

from sqlalchemy import (
    CheckConstraint,
    ForeignKey,
    Index,
    Integer,
    String,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.config import get_config
from app.db.base import Base

# TODO: Introduce retention policy for file revisions. Define rules
# (e.g., max revisions, time-based cleanup, pinned revisions) and
# enforce them at the service layer.

# NOTE (ADR-51): File stores current state; revision stores history.
# File represents the current version, while file revision keeps only
# previous immutable versions. When a new upload replaces the current
# state, the previous state must be copied to revision before updating
# file.

# NOTE (ADR-55): Revision created_by identifies creator, not owner.
# It refers to the user who created the revision and does not imply
# ownership. Access control is determined by RBAC.


class FileRevision(Base):
    __tablename__ = "files_revisions"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    file_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("files.id", ondelete="RESTRICT"),
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

    revision_number: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        server_default=text("1"),
    )

    # Physical filename on disk (UUID used as storage key)
    revision_uuid: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True,
    )

    # Filename at the time the revision was created
    filename: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    filesize: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        server_default=text("0"),
    )

    mimetype: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    checksum: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
    )

    revision_file: Mapped["File"] = relationship(  # noqa: F821
        "File",
        back_populates="file_revisions",
    )

    revision_created_by_user: Mapped["User"] = relationship(  # noqa: F821
        "User",
        foreign_keys=[created_by],
        lazy="selectin",
    )

    __table_args__ = (
        CheckConstraint(
            "revision_number >= 1",
            name="ck_files_revisions_revision_number_positive",
        ),
        CheckConstraint(
            "filesize >= 0",
            name="ck_files_revisions_filesize_non_negative",
        ),
        Index(
            "uq_files_revisions_file_id_revision_number",
            "file_id",
            "revision_number",
            unique=True,
        ),
        {"sqlite_autoincrement": True},
    )

    @property
    def absolute_path(self) -> str:
        """
        Return the absolute filesystem path of this file revision.
        The path is constructed by joining the configured revisions
        directory with the stored revision UUID.
        Example: /var/lib/hidden/mountpoint/revisions/550e8400-e29b-41d4
        """
        config = get_config()

        return os.path.join(
            config.FILES_REVISIONS_DIR,
            self.revision_uuid,
        )
