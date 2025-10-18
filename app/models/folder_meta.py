"""SQLAlchemy model for folder metadata."""

import time
from sqlalchemy import (
    Column, Integer, BigInteger, String, ForeignKey, UniqueConstraint
)
from sqlalchemy.orm import relationship
from app.sqlite import Base


class FolderMeta(Base):
    """
    SQLAlchemy model for folder metadata. Stores a key-value pair
    linked to a folder; keys are unique within each folder.
    """

    __tablename__ = "folders_meta"
    __table_args__ = (
        UniqueConstraint(
            "folder_id", "meta_key",
            name="uq_folders_meta_folder_id_meta_key"
        ),
        {"sqlite_autoincrement": True},
    )
    _cacheable = False

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    folder_id = Column(
        Integer,
        ForeignKey("folders.id", ondelete="CASCADE"),
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

    meta_key = Column(
        String(128),
        nullable=False
    )

    meta_value = Column(
        String(4096),
        nullable=True
    )

    meta_folder = relationship(
        "Folder",
        back_populates="folder_meta"
    )
