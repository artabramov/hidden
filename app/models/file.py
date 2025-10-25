"""SQLAlchemy model for files."""

import time
import os
from typing import Any
from sqlalchemy import (
    Column, BigInteger, String, Boolean, Integer, ForeignKey, UniqueConstraint)
from sqlalchemy.orm import relationship
from app.sqlite import Base
from app.models.file_meta import FileMeta  # noqa: F401
from app.models.file_tag import FileTag  # noqa: F401
from app.models.file_thumbnail import FileThumbnail  # noqa: F401
from app.models.file_revision import FileRevision  # noqa: F401


class File(Base):

    __tablename__ = "files"
    __table_args__ = (
        UniqueConstraint(
            "folder_id", "filename",
            name="uq_files_folder_id_filename"
        ),
        {"sqlite_autoincrement": True},
    )
    _cacheable = True

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )

    folder_id = Column(
        Integer,
        ForeignKey("folders.id"),
        nullable=False,
        index=True,
    )

    created_date = Column(
        BigInteger,
        nullable=False,
        index=True,
        default=lambda: int(time.time())
    )

    updated_date = Column(
        BigInteger,
        nullable=False,
        index=True,
        default=lambda: int(time.time()),
        onupdate=lambda: int(time.time())
    )

    flagged = Column(
        Boolean,
        nullable=False,
        default=False
    )

    filename = Column(
        String(256),
        index=True,
        nullable=False
    )

    filesize = Column(
        Integer,
        index=True,
        nullable=False
    )

    mimetype = Column(
        String(256),
        index=True,
        nullable=True
    )

    checksum = Column(
        String(64),
        nullable=False
    )

    summary = Column(
        String(4096),
        nullable=True
    )

    latest_revision_number = Column(
        Integer,
        nullable=False,
        default=0
    )

    file_user = relationship(
        "User",
        back_populates="user_files",
        lazy="joined"
    )

    file_folder = relationship(
        "Folder",
        back_populates="folder_files",
        lazy="joined"
    )

    file_meta = relationship(
        "FileMeta",
        back_populates="meta_file",
        cascade="all, delete-orphan",
        lazy="selectin",
        passive_deletes=True
    )

    file_tags = relationship(
        "FileTag",
        back_populates="tag_file",
        cascade="all, delete-orphan",
        lazy="selectin",
        passive_deletes=True
    )

    file_thumbnail = relationship(
        "FileThumbnail",
        back_populates="thumbnail_file",
        cascade="all, delete-orphan",
        uselist=False,
        lazy="joined"
    )

    file_revisions = relationship(
        "FileRevision",
        back_populates="revision_file",
        cascade="all, delete-orphan",
        lazy="selectin",
        passive_deletes=True
    )

    def __init__(
            self, user_id: int, folder_id: int, filename: str,
            filesize: int, checksum: str, mimetype: str = None,
            flagged: bool = False, summary: str = None,
            latest_revision_number: int = 0):
        self.user_id = user_id
        self.folder_id = folder_id
        self.filename = filename
        self.filesize = filesize
        self.mimetype = mimetype
        self.checksum = checksum
        self.flagged = flagged
        self.summary = summary
        self.latest_revision_number = latest_revision_number

    @property
    def has_thumbnail(self) -> bool:
        return self.file_thumbnail is not None

    @property
    def has_revisions(self) -> bool:
        return len(self.file_revisions) > 0

    @classmethod
    def path_for_filename(cls, config: Any, folder_name: str,
                          filename: str) -> str:
        """Return absolute path to the file file by parameters."""
        return os.path.join(config.FILES_DIR, folder_name, filename)

    def path(self, config: Any) -> str:
        """Return absolute path to the file file by config."""
        return self.__class__.path_for_filename(
            config, self.file_folder.name, self.filename)

    async def to_dict(self) -> dict:
        """Returns a dictionary representation of the file."""
        return {
            "id": self.id,
            "user": await self.file_user.to_dict(),
            "folder": await self.file_folder.to_dict(),
            "created_date": self.created_date,
            "updated_date": self.updated_date,
            "flagged": self.flagged,
            "filename": self.filename,
            "filesize": self.filesize,
            "mimetype": self.mimetype,
            "checksum": self.checksum,
            "summary": self.summary,
            "latest_revision_number": self.latest_revision_number,
            "has_thumbnail": self.has_thumbnail,
            "file_revisions": [
                await revision.to_dict() for revision
                in self.file_revisions
            ],
            "file_tags": [t.value for t in self.file_tags],
        }
