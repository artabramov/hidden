"""SQLAlchemy model for file revisions."""

import os
import time
from typing import Any
from sqlalchemy import (
    Column, Integer, BigInteger, String, ForeignKey, UniqueConstraint)
from sqlalchemy.orm import relationship
from app.sqlite import Base


class FileRevision(Base):
    """
    SQLAlchemy model for file revisions. Immutable snapshots of a file.
    """

    __tablename__ = "files_revisions"
    __table_args__ = (
        UniqueConstraint(
            "file_id", "revision_number",
            name="uq_files_revisions_file_id_revision_number"
        ),
        {"sqlite_autoincrement": True},
    )
    _cacheable = False

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

    file_id = Column(
        Integer,
        ForeignKey("files.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    created_date = Column(
        BigInteger,
        nullable=False,
        index=True,
        default=lambda: int(time.time())
    )

    revision_number = Column(
        Integer,
        nullable=False,
        index=True,
    )

    uuid = Column(
        String(256),
        index=True,
        nullable=False
    )

    filesize = Column(
        Integer,
        nullable=False,
        index=True
    )

    checksum = Column(
        String(64),
        nullable=False,
        index=True
    )

    # NOTE: Join users because revisions themselves are not cached;
    # they should be cached as part of files and contain users.
    revision_user = relationship(
        "User",
        back_populates="user_revisions",
        uselist=False,
        lazy="joined"
    )

    revision_file = relationship(
        "File",
        back_populates="file_revisions"
    )

    @classmethod
    def path_for_uuid(cls, config: Any, uuid: str) -> str:
        """Return absolute path for a given UUID using config."""
        return os.path.join(config.REVISIONS_DIR, uuid)

    def path(self, config: Any) -> str:
        """Return absolute path to the thumbnail file by its UUID."""
        return self.__class__.path_for_uuid(config, self.uuid)

    def __init__(
            self, user_id: int, file_id: int, revision_number: int,
            uuid: str, filesize: int, checksum: str):
        self.user_id = user_id
        self.file_id = file_id
        self.revision_number = revision_number
        self.uuid = uuid
        self.filesize = filesize
        self.checksum = checksum

    async def to_dict(self) -> dict:
        """Returns a dictionary representation of the revision."""
        return {
            "id": self.id,
            "user": await self.revision_user.to_dict(),
            "file_id": self.file_id,
            "created_date": self.created_date,
            "revision_number": self.revision_number,
            "uuid": self.uuid,
            "filesize": self.filesize,
            "checksum": self.checksum,
        }
