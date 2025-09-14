"""SQLAlchemy model for documents."""

import time
from sqlalchemy import (
    Column, BigInteger, String, Boolean, Integer, ForeignKey, UniqueConstraint)
from sqlalchemy.orm import relationship
from app.sqlite import Base
from app.models.document_meta import DocumentMeta  # noqa: F401
from app.models.document_tag import DocumentTag  # noqa: F401
from app.models.document_thumbnail import DocumentThumbnail  # noqa: F401
from app.models.document_revision import DocumentRevision  # noqa: F401


class Document(Base):

    __tablename__ = "documents"
    __table_args__ = (
        UniqueConstraint(
            "collection_id", "filename",
            name="uq_documents_collection_id_filename"
        ),
        {"sqlite_autoincrement": True},
    )
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

    collection_id = Column(
        Integer,
        ForeignKey("collections.id"),
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

    flagged = Column(
        Boolean,
        nullable=False,
        default=False
    )

    filename = Column(
        String(256),
        index=True,
        nullable=False
    )

    filesize = Column(
        Integer,
        index=True,
        nullable=False
    )

    mimetype = Column(
        String(256),
        index=True,
        nullable=True
    )

    checksum = Column(
        String(64),
        nullable=False
    )

    summary = Column(
        String(4096),
        nullable=True
    )

    latest_revision_number = Column(
        Integer,
        nullable=False,
        default=0
    )

    document_user = relationship(
        "User",
        back_populates="user_documents",
        lazy="joined"
    )

    document_collection = relationship(
        "Collection",
        back_populates="collection_documents",
        lazy="joined"
    )

    document_meta = relationship(
        "DocumentMeta",
        back_populates="meta_document",
        cascade="all, delete-orphan",
        lazy="selectin",
        passive_deletes=True
    )

    document_tags = relationship(
        "DocumentTag",
        back_populates="tag_document",
        cascade="all, delete-orphan",
        lazy="selectin",
        passive_deletes=True
    )

    document_thumbnail = relationship(
        "DocumentThumbnail",
        back_populates="thumbnail_document",
        cascade="all, delete-orphan",
        uselist=False,
        lazy="joined"
    )

    document_revisions = relationship(
        "DocumentRevision",
        back_populates="revision_document",
        cascade="all, delete-orphan",
        lazy="selectin",
        passive_deletes=True
    )

    def __init__(
            self, user_id: int, collection_id: int, filename: str,
            filesize: int, checksum: str, mimetype: str = None,
            flagged: bool = False, summary: str = None,
            latest_revision_number: int = 0):
        self.user_id = user_id
        self.collection_id = collection_id
        self.filename = filename
        self.filesize = filesize
        self.mimetype = mimetype
        self.checksum = checksum
        self.flagged = flagged
        self.summary = summary
        self.latest_revision_number = latest_revision_number

    @property
    def has_thumbnail(self) -> bool:
        return self.document_thumbnail is not None

    async def to_dict(self) -> dict:
        """Returns a dictionary representation of the document."""
        return {
            "id": self.id,
            "user": await self.document_user.to_dict(),
            "collection": await self.document_collection.to_dict(),
            "created_date": self.created_date,
            "updated_date": self.updated_date,
            "flagged": self.flagged,
            "filename": self.filename,
            "filesize": self.filesize,
            "mimetype": self.mimetype,
            "checksum": self.checksum,
            "summary": self.summary,
            "latest_revision_number": self.latest_revision_number,
            "document_revisions": [
                await revision.to_dict() for revision
                in self.document_revisions
            ],
        }
