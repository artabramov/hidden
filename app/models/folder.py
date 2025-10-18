"""SQLAlchemy model for folders."""

import time
import os
from typing import Any
from sqlalchemy import Column, BigInteger, String, Boolean, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.sqlite import Base
from app.models.folder_meta import FolderMeta  # noqa: F401


class Folder(Base):
    """
    SQLAlchemy model for folders. Stores a unique name, read-only
    flag, creation/update timestamps, and optional summary.
    """
    __tablename__ = "folders"
    __table_args__ = {"sqlite_autoincrement": True}
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

    readonly = Column(
        Boolean,
        nullable=False,
    )

    name = Column(
        String(256),
        nullable=False,
        unique=True
    )

    summary = Column(
        String(4096),
        nullable=True
    )

    folder_meta = relationship(
        "FolderMeta",
        back_populates="meta_folder",
        cascade="all, delete-orphan",
        lazy="selectin",
        passive_deletes=True
    )

    folder_user = relationship(
        "User",
        back_populates="user_folders",
        lazy="joined"
    )

    folder_files = relationship(
        "File",
        back_populates="file_folder",
        lazy="noload"
    )

    def __init__(self, user_id: int, readonly: bool, name: str,
                 summary: str = None):
        self.user_id = user_id
        self.readonly = readonly
        self.name = name
        self.summary = summary

    @classmethod
    def path_for_dir(cls, config: Any, folder_name: str) -> str:
        """Return absolute path to the folder by parameters."""
        return os.path.join(config.FILES_DIR, folder_name)

    def path(self, config: Any) -> str:
        """Return absolute path to the folder by config."""
        return self.__class__.path_for_dir(config, self.name)

    async def to_dict(self) -> dict:
        """Returns a dictionary representation of the folder."""
        return {
            "id": self.id,
            "user": await self.folder_user.to_dict(),
            "created_date": self.created_date,
            "updated_date": self.updated_date,
            "readonly": self.readonly,
            "name": self.name,
            "summary": self.summary,
        }
