# app/models/file_thumbnail.py
# SPDX-License-Identifier: SSPL-1.0

import os
import time

from sqlalchemy import (
    CheckConstraint,
    ForeignKey,
    Index,
    Integer,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.config import get_config
from app.db.base import Base

# NOTE (ADR-57): Thumbnails are derived artifacts stored by storage keys.
# Thumbnails are preview artifacts for GUI usage. Files are stored in
# a flat directory and addressed by UUID-like storage keys, not by
# original filenames.


class FileThumbnail(Base):
    __tablename__ = "files_thumbnails"

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

    # Storage filename in thumbnails/ directory.
    thumbnail_uuid: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True,
    )

    filesize: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    mimetype: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    width: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    height: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    thumbnail_file: Mapped["File"] = relationship(  # noqa: F821
        "File",
        back_populates="file_thumbnail",
        lazy="selectin",
    )

    thumbnail_created_by_user: Mapped["User"] = relationship(  # noqa: F821
        "User",
        foreign_keys=[created_by],
        lazy="selectin",
    )

    __table_args__ = (
        CheckConstraint(
            "filesize > 0",
            name="ck_files_thumbnails_filesize_positive",
        ),
        CheckConstraint(
            "width > 0",
            name="ck_files_thumbnails_width_positive",
        ),
        CheckConstraint(
            "height > 0",
            name="ck_files_thumbnails_height_positive",
        ),
        Index(
            "uq_files_thumbnails_file_id",
            "file_id",
            unique=True,
        ),
        {"sqlite_autoincrement": True},
    )

    @property
    def absolute_path(self) -> str:
        """
        Return the absolute filesystem path of this thumbnail file.
        The path is constructed by joining the configured thumbnails
        directory with the stored thumbnail UUID.
        """
        config = get_config()

        return os.path.join(
            config.FILES_THUMBNAILS_DIR,
            self.thumbnail_uuid,
        )
