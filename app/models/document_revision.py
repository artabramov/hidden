"""SQLAlchemy model for document revisions."""

import time
from sqlalchemy import (
    Column, Integer, BigInteger, String, ForeignKey, UniqueConstraint)
from sqlalchemy.orm import relationship
from app.sqlite import Base

class DocumentRevision(Base):
    """
    SQLAlchemy model for document revisions.
    Immutable snapshots of a document.
    """

    __tablename__ = "documents_revisions"
    __table_args__ = (
        UniqueConstraint(
            "document_id", "revision_number",
            name="uq_documents_revisions_document_id_revision_number"
        ),
        {"sqlite_autoincrement": True},
    )
    _cacheable = False

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

    document_id = Column(
        Integer,
        ForeignKey("documents.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    created_date = Column(
        BigInteger,
        nullable=False,
        index=True,
        default=lambda: int(time.time())
    )

    revision_number = Column(
        Integer,
        nullable=False,
        index=True,
    )

    uuid = Column(
        String(256),
        index=True,
        nullable=False
    )

    filesize = Column(
        Integer,
        nullable=False,
        index=True
    )

    checksum = Column(
        String(64),
        nullable=False,
        index=True
    )

    # NOTE: Join users because revisions themselves are not cached;
    # they should be cached as part of documents and contain users.
    revision_user = relationship(
        "User",
        back_populates="user_revisions",
        uselist=False,
        lazy="joined"
    )

    revision_document = relationship(
        "Document",
        back_populates="document_revisions"
    )

    def __init__(
            self, user_id: int, document_id: int, revision_number: int,
            uuid: str, filesize: int, checksum: str):
        self.user_id = user_id
        self.document_id = document_id
        self.revision_number = revision_number
        self.uuid = uuid
        self.filesize = filesize
        self.checksum = checksum

    async def to_dict(self) -> dict:
        """Returns a dictionary representation of the revision."""
        return {
            "id": self.id,
            "user": await self.revision_user.to_dict(),
            "document_id": self.document_id,
            "created_date": self.created_date,
            "revision_number": self.revision_number,
            "uuid": self.uuid,
            "filesize": self.filesize,
            "checksum": self.checksum,
        }
