"""SQLAlchemy model for document thumbnails."""

import time
from sqlalchemy import (
    Column, Integer, BigInteger, SmallInteger, String, ForeignKey)
from sqlalchemy.orm import relationship
from app.sqlite import Base


class DocumentThumbnail(Base):
    """
    SQLAlchemy model for document thumbnails. One-to-one thumbnail
    linked to a document; stores file name, size, type, dimensions,
    and checksum.
    """

    __tablename__ = "documents_thumbnails"
    __table_args__ = {"sqlite_autoincrement": True}

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
        String(128),
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

    thumbnail_document = relationship(
        "Document",
        back_populates="document_thumbnail"
    )

    def __init__(self, document_id: int, filename: str, width: int,
                 height: int, checksum: str, filesize: int, mimetype: str):
        self.document_id = document_id
        self.filename = filename
        self.width = width
        self.height = height
        self.checksum = checksum
        self.filesize = filesize
        self.mimetype = mimetype
