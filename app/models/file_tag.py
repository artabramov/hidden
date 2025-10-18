"""SQLAlchemy model for file tags."""

import time
from sqlalchemy import (
    Column, Integer, BigInteger, String, ForeignKey, UniqueConstraint
)
from sqlalchemy.orm import relationship
from app.sqlite import Base


class FileTag(Base):
    """
    SQLAlchemy model for file tags. Stores a tag value linked
    to a file; values are unique within each file.
    """

    __tablename__ = "files_tags"
    __table_args__ = (
        UniqueConstraint(
            "file_id", "value",
            name="uq_files_tags_file_id_value"
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

    value = Column(
        String(40),
        nullable=False,
        index=True
    )

    tag_file = relationship(
        "File",
        back_populates="file_tags"
    )

    def __init__(self, file_id: int, value: str):
        self.file_id = file_id
        self.value = value
