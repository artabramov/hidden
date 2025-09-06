"""
Thumbnails for users: each user has a single avatar stored as binary data
with metadata and audit timestamps.
"""

import time
from sqlalchemy import (
    Column, Integer, BigInteger, SmallInteger, String, ForeignKey)
from sqlalchemy.orm import relationship
from app.sqlite import Base


class UserThumbnail(Base):
    """
    SQLAlchemy model for user thumbnails (avatars).
    Each user has at most one thumbnail linked via user_id.
    """
    __tablename__ = "users_thumbnails"
    __table_args__ = {"sqlite_autoincrement": True}

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

    mimetype = Column(
        String(80),
        nullable=True
    )

    width = Column(
        SmallInteger,
        nullable=False
    )
    
    height = Column(
        SmallInteger,
        nullable=False
    )

    checksum = Column(
        String(64),
        nullable=False
    )

    thumbnail_user = relationship(
        "User",
        back_populates="user_thumbnail"
    )

    def __init__(self, user_id: int, filename: str, width: int, height: int,
                 checksum: str, filesize: int, mimetype: str):
        """
        Initialize a user thumbnail entity with required metadata.
        """
        self.user_id = user_id
        self.filename = filename
        self.width = width
        self.height = height
        self.checksum = checksum
        self.filesize = filesize
        self.mimetype = mimetype
