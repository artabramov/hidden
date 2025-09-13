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
            "document_id", "revision",
            name="uq_documents_revisions_document_id_revision"
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

    revision = Column(
        Integer,
        nullable=False,
        index=True,
    )

    filename = Column(
        String(256),
        nullable=False,
        index=True
    )

    filesize = Column(
        Integer,
        nullable=False,
        index=True
    )

    mimetype = Column(
        String(256),
        nullable=True,
        index=True
    )

    checksum = Column(
        String(64),
        nullable=False,
        index=True
    )

    revision_user = relationship(
        "User",
        back_populates="user_revisions"
    )

    revision_document = relationship(
        "Document",
        back_populates="document_revisions"
    )

    def __init__(
            self, user_id: int, document_id: int, revision: int,
            filename: str, filesize: int, checksum: str,
            mimetype: str = None):
        self.user_id = user_id
        self.document_id = document_id
        self.revision = revision
        self.filename = filename
        self.filesize = filesize
        self.mimetype = mimetype
        self.checksum = checksum
