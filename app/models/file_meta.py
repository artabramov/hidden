"""SQLAlchemy model for file metadata."""

import time
from sqlalchemy import (
    Column, Integer, BigInteger, String, ForeignKey, UniqueConstraint
)
from sqlalchemy.orm import relationship
from app.sqlite import Base


class FileMeta(Base):
    """
    SQLAlchemy model for file metadata. Stores a key-value pair linked
    to a file; keys are unique within each file.
    """

    __tablename__ = "files_meta"
    __table_args__ = (
        UniqueConstraint(
            "file_id", "meta_key",
            name="uq_files_meta_file_id_meta_key"
        ),
        {"sqlite_autoincrement": True},
    )
    _cacheable = False

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    file_id = Column(
        Integer,
        ForeignKey("files.id", ondelete="CASCADE"),
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

    meta_file = relationship(
        "File",
        back_populates="file_meta"
    )
