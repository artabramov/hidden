# app/models/file.py
# SPDX-License-Identifier: SSPL-1.0

import os
import time
from enum import StrEnum
from pathlib import PurePosixPath

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.config import get_config
from app.db.base import Base
from app.repositories.file import isimage, istext

# TODO: Detect suspicious files by mismatch between filename/mimetype
# and actual content (e.g., magic bytes). Add validation and reporting
# at upload/revision creation stage.

# NOTE (ADR-43): Database is source of truth; filesystem is projection.
# The gocryptfs filesystem reflects database state and is not
# authoritative. Folder deletion is performed only via service-layer
# logic, with explicit handling of nested folders, files, revisions,
# and thumbnails.

# NOTE (ADR-50): File created_by/updated_by identify actors, not owners.
# They refer to the users who created and last modified the entity and
# do not imply ownership. Access control is determined by RBAC, not by
# ownership.

# NOTE (ADR-53): File updated_at reflects all modifications.
# It tracks the last change to the file entity, including metadata
# updates (rename, move, summary, is_starred) and content changes
# (creation of a new file revision).


class FileType(StrEnum):
    IMAGE = "image"
    TEXT = "text"
    BINARY = "binary"


class File(Base):
    __tablename__ = "files"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    folder_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("folders.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    created_by: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    updated_by: Mapped[int] = mapped_column(
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

    is_starred: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text("0"),
        index=True,
    )

    filename: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
    )

    filesize: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        server_default=text("0"),
        index=True,
    )

    mimetype: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        index=True,
    )

    checksum: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
    )

    summary: Mapped[str | None] = mapped_column(
        String(4096),
        nullable=True,
    )

    comments_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        server_default=text("0"),
    )

    latest_revision_number: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        server_default=text("0"),
    )

    file_created_by_user: Mapped["User"] = relationship(  # noqa: F821
        "User",
        foreign_keys=[created_by],
        lazy="selectin",
    )

    file_updated_by_user: Mapped["User | None"] = relationship(  # noqa: F821
        "User",
        foreign_keys=[updated_by],
        lazy="selectin",
    )

    file_revisions: Mapped[list["FileRevision"]] = relationship(  # noqa: F821
        "FileRevision",
        order_by="FileRevision.revision_number.desc()",
        back_populates="revision_file",
        lazy="selectin",
    )

    file_folder: Mapped["Folder"] = relationship(  # noqa: F821
        "Folder",
        back_populates="folder_files",
        lazy="selectin",
    )

    file_comments: Mapped[list["FileComment"]] = relationship(  # noqa: F821
        "FileComment",
        back_populates="comment_file",
        order_by="FileComment.created_at.asc()",
        cascade="all, delete-orphan",
        passive_deletes=True,
        lazy="selectin",
    )

    file_tags: Mapped[list["FileTag"]] = relationship(  # noqa: F821
        "FileTag",
        back_populates="tag_file",
        order_by="FileTag.tag.asc()",
        cascade="all, delete-orphan",
        passive_deletes=True,
        lazy="selectin",
    )

    file_thumbnail: Mapped["FileThumbnail | None"] = relationship(  # noqa: E501, F821
        "FileThumbnail",
        back_populates="thumbnail_file",
        uselist=False,
        lazy="selectin",
    )

    __table_args__ = (
        CheckConstraint(
            "filesize >= 0",
            name="ck_files_filesize_non_negative",
        ),
        CheckConstraint(
            "comments_count >= 0",
            name="ck_files_comments_count_non_negative",
        ),
        CheckConstraint(
            "latest_revision_number >= 0",
            name="ck_files_latest_revision_number_non_negative",
        ),
        UniqueConstraint(
            "folder_id",
            "filename",
            name="uq_file_folder_filename"
        ),
        {"sqlite_autoincrement": True},
    )

    @property
    def has_thumbnail(self) -> bool:
        """Return True if this file has an associated thumbnail row."""
        return self.file_thumbnail is not None

    @property
    def is_image(self) -> bool:
        """Return True if the file is a supported image."""
        return isimage(self.mimetype)

    @property
    def is_text(self) -> bool:
        """Return True if the file is a text file."""
        return istext(self.mimetype)

    @property
    def filetype(self) -> FileType:
        """Return file type derived from MIME type."""
        if self.is_image:
            return FileType.IMAGE
        if self.is_text:
            return FileType.TEXT
        return FileType.BINARY

    def get_relative_path(
        self,
        folder: "Folder",  # noqa: F821
        folder_parent_chain: tuple["Folder", ...],  # noqa: F821
    ) -> str:
        """
        Return the relative path of this file within the files tree.
        """
        return str(PurePosixPath(
            folder._get_relative_dir(folder_parent_chain),
            self.filename,
        ))

    def get_absolute_path(
        self,
        folder: "Folder",  # noqa: F821
        folder_parent_chain: tuple["Folder", ...],  # noqa: F821
    ) -> str:
        """
        Return the absolute filesystem path of this file.
        """
        config = get_config()

        return os.path.join(
            config.FILES_DIR,
            self.get_relative_path(folder, folder_parent_chain),
        )
