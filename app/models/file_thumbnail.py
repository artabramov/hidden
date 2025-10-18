"""SQLAlchemy model for file thumbnails."""

import time
from sqlalchemy import Column, Integer, BigInteger, String, ForeignKey
from sqlalchemy.orm import relationship
from app.sqlite import Base
from app.helpers.thumbnail_mixin import ThumbnailMixin


class FileThumbnail(Base, ThumbnailMixin):
    """
    SQLAlchemy model for file thumbnails. One-to-one thumbnail
    linked to a file; stores UUID (thumbnail file name), file
    size, and checksum.
    """

    # NOTE: Thumbnail models are obtained only through parent files;
    # the file cache applies and thumbnail cache is not necessary.

    __tablename__ = "files_thumbnails"
    __table_args__ = {"sqlite_autoincrement": True}
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

    uuid = Column(
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

    thumbnail_file = relationship(
        "File",
        back_populates="file_thumbnail"
    )

    def __init__(self, file_id: int, uuid: str, filesize: int,
                 checksum: str):
        """Initialize a file thumbnail entity."""
        self.file_id = file_id
        self.uuid = uuid
        self.filesize = filesize
        self.checksum = checksum
