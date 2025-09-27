"""SQLAlchemy model for document thumbnails."""

import time
from sqlalchemy import Column, Integer, BigInteger, String, ForeignKey
from sqlalchemy.orm import relationship
from app.sqlite import Base
from app.helpers.thumbnail_mixin import ThumbnailMixin


class DocumentThumbnail(Base, ThumbnailMixin):
    """
    SQLAlchemy model for document thumbnails. One-to-one thumbnail
    linked to a document; stores UUID (thumbnail file name), file
    size, and checksum.
    """

    # NOTE: Thumbnail models are obtained only through parent documents;
    # the document cache applies and thumbnail cache is not necessary.

    __tablename__ = "documents_thumbnails"
    __table_args__ = {"sqlite_autoincrement": True}
    _cacheable = False

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    document_id = Column(
        Integer,
        ForeignKey("documents.id", ondelete="CASCADE"),
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

    thumbnail_document = relationship(
        "Document",
        back_populates="document_thumbnail"
    )

    def __init__(self, document_id: int, uuid: str, filesize: int,
                 checksum: str):
        """Initialize a document thumbnail entity."""
        self.document_id = document_id
        self.uuid = uuid
        self.filesize = filesize
        self.checksum = checksum
