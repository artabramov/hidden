"""SQLAlchemy model for user thumbnails."""

import time
from sqlalchemy import Column, Integer, BigInteger, String, ForeignKey
from sqlalchemy.orm import relationship
from app.sqlite import Base


class UserThumbnail(Base):
    """
    SQLAlchemy model for user thumbnails. One-to-one thumbnail
    linked to a user; stores file name, size, type, dimensions,
    and checksum.
    """
    __tablename__ = "users_thumbnails"
    __table_args__ = {"sqlite_autoincrement": True}
    _cacheable = False

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
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

    filename = Column(
        String(256),
        index=True,
        nullable=False
    )

    filesize = Column(
        Integer,
        nullable=False,
        default=0
    )

    checksum = Column(
        String(64),
        nullable=False
    )

    thumbnail_user = relationship(
        "User",
        back_populates="user_thumbnail"
    )

    def __init__(self, user_id: int, filename: str, filesize: int,
                 checksum: str):
        """
        Initialize a user thumbnail entity with required metadata.
        """
        self.user_id = user_id
        self.filename = filename
        self.filesize = filesize
        self.checksum = checksum
