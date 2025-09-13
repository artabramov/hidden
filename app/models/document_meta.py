"""SQLAlchemy model for document metadata."""

import time
from sqlalchemy import (
    Column, Integer, BigInteger, String, ForeignKey, UniqueConstraint
)
from sqlalchemy.orm import relationship
from app.sqlite import Base


class DocumentMeta(Base):
    """
    SQLAlchemy model for document metadata. Stores a key-value pair
    linked to a document; keys are unique within each document.
    """

    __tablename__ = "documents_meta"
    __table_args__ = (
        UniqueConstraint(
            "document_id", "meta_key",
            name="uq_documents_meta_document_id_meta_key"
        ),
        {"sqlite_autoincrement": True},
    )
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

    meta_document = relationship(
        "Document",
        back_populates="document_meta"
    )
