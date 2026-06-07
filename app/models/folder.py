# app/models/folder.py
# SPDX-License-Identifier: SSPL-1.0

import os
import time
from pathlib import PurePosixPath

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    ForeignKey,
    Index,
    Integer,
    String,
    func,
    literal,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.config import get_config
from app.db.base import Base

# NOTE (ADR-45): Filesystem path constraints are enforced.
# Folder depth and full path length (in UTF-8 bytes) are limited
# according to filesystem bounds (PATH_MAX, 4096 bytes). Validation
# is performed at the service layer before any FS operation.

# NOTE (ADR-54): File/folder logic uses explicit parent chain.
# Methods such as is_write_protected_recursive and get_absolute_dir
# accept a pre-fetched parent_chain instead of using lazy-loaded
# relationships. This avoids implicit async I/O (greenlet issues) when
# such logic is accessed from synchronous contexts (e.g. properties or
# model methods).

# NOTE (ADR-59): Folder name uniqueness includes root.
# SQLite treats NULL as distinct in UNIQUE(parent_id, name), allowing
# duplicate names at the root. A functional unique index that coalesces
# parent_id to a sentinel enforces uniqueness at the root as well.

# NOTE (ADR-60): Folder deletion is service-layer controlled.
# Direct DELETE is not allowed due to filesystem consistency.
# Folder deletion removes direct files but does not recursively delete
# subfolders; folders containing subfolders are rejected.

# NOTE (ADR-61): Folder write protection is an additional restriction.
# The is_write_protected flag acts as an administrative override and
# does not replace role-based permissions. If a folder is protected,
# all write operations are forbidden regardless of user role. The
# restriction is recursive and applies to the subtree, including all
# nested folders and files at any depth.

# NOTE (ADR-62): Folder child counters are denormalized direct counters.
# children_count and files_count track direct children only (not subtree
# totals). Maintained by service-layer writes under directory WRITE
# locks. The virtual root is implicit; totals are computed separately.

# NOTE (ADR-63): Folder move/copy operations are not supported.
# This is a product-level trade-off: folders act as a stable hierarchy,
# while bulk file operations cover user needs. The filesystem is a
# projection of the database, not the source of truth. Folder move/copy
# would affect entire subtrees and significantly increase complexity.
# Given these constraints, folder move/copy is deliberately excluded
# to keep the domain model simple, predictable, and safe.
# Supporting folder move/copy would require:
# 1. cycle detection within the folder tree;
# 2. recursive write protection checks for source and target branches;
# 3. depth recalculation and validation;
# 4. full-subtree path validation (not just the root folder);
# 5. synchronized DB and filesystem tree move;
# 6. rollback handling for partially applied filesystem changes;
# 7. hierarchical locking (source subtree + target parent);
# 8. conflict resolution for nested folders;
# 9. preserving audit and hook semantics across affected entities.


class Folder(Base):
    """
    Folder node in the storage. The database is the source of truth;
    the on-disk layout mirrors names under gocryptfs. Hard delete only.
    """

    __tablename__ = "folders"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    parent_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("folders.id", ondelete="RESTRICT"),
        nullable=True,
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
    )

    updated_at: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        onupdate=lambda: int(time.time()),
    )

    # Current folder (directory) name
    dirname: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
    )

    is_write_protected: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text("0"),
    )

    summary: Mapped[str | None] = mapped_column(
        String(4096),
        nullable=True,
    )

    children_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        server_default=text("0"),
    )

    files_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        server_default=text("0"),
    )

    folder_parent: Mapped["Folder | None"] = relationship(
        "Folder",
        remote_side="Folder.id",
        back_populates="folder_children",
        lazy="selectin",
    )

    folder_children: Mapped[list["Folder"]] = relationship(
        "Folder",
        back_populates="folder_parent",
        lazy="selectin",
    )

    folder_files: Mapped[list["File"]] = relationship(  # noqa: F821
        "File",
        back_populates="file_folder",
        lazy="selectin",
    )

    folder_created_by_user: Mapped["User"] = relationship(  # noqa: F821
        "User",
        foreign_keys=[created_by],
        lazy="selectin",
    )

    folder_updated_by_user: Mapped["User | None"] = relationship(  # noqa: F821
        "User",
        foreign_keys=[updated_by],
        lazy="selectin",
    )

    __table_args__ = (
        Index(
            "uq_folders_parent_id_dirname",
            func.coalesce(parent_id, literal(-1)),
            dirname,
            unique=True,
        ),
        CheckConstraint(
            "children_count >= 0",
            name="ck_folders_children_count_non_negative",
        ),
        CheckConstraint(
            "files_count >= 0",
            name="ck_folders_files_count_non_negative",
        ),
        {"sqlite_autoincrement": True},
    )

    def is_write_protected_recursive(
        self,
        parent_chain: tuple["Folder", ...],
    ) -> bool:
        """
        Return whether any parent folder in the chain is write-protected.
        The current folder's own flag is not considered here; use
        is_write_protected directly for that check.
        The parent chain must be ordered from immediate parent to root.
        """
        self._validate_parent_chain(parent_chain)
        return any(
            folder.is_write_protected for folder in parent_chain
        )

    def get_absolute_dir(
        self,
        parent_chain: tuple["Folder", ...],
    ) -> str:
        """
        Return the absolute filesystem path of this folder.
        The parent chain must be ordered from immediate parent to root.
        """
        config = get_config()
        return os.path.join(
            config.FILES_DIR,
            self._get_relative_dir(parent_chain),
        )

    def _get_relative_dir(
        self,
        parent_chain: tuple["Folder", ...],
    ) -> str:
        """
        Return the relative path of this folder within the files tree.
        The parent chain must be ordered from immediate parent to root.
        """
        self._validate_parent_chain(parent_chain)

        parts = [parent.dirname for parent in reversed(parent_chain)]
        parts.append(self.dirname)

        return str(PurePosixPath(*parts))

    def _validate_parent_chain(
        self,
        parent_chain: tuple["Folder", ...],
    ) -> None:
        """
        Validate parent chain integrity: no cycles; correct linkage
        via parent_id; correct order from immediate parent to root.
        """
        if not parent_chain:
            if self.parent_id is not None:
                raise ValueError("Parent chain is required")
            return

        seen: set[int] = set()

        first = parent_chain[0]
        if first.id != self.parent_id:
            raise ValueError("First element is not direct parent")

        prev = self

        for folder in parent_chain:
            if folder.id in seen:
                raise ValueError("Cycle detected in folder tree")

            seen.add(folder.id)

            if folder.id != prev.parent_id:
                raise ValueError("Invalid parent chain linkage")

            prev = folder
