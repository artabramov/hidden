"""SQLAlchemy model for document tags."""

import time
from sqlalchemy import (
    Column, Integer, BigInteger, String, ForeignKey, UniqueConstraint
)
from sqlalchemy.orm import relationship
from app.sqlite import Base


class DocumentTag(Base):
    """
    SQLAlchemy model for document tags. Stores a tag value linked
    to a document; values are unique within each document.
    """

    __tablename__ = "documents_tags"
    __table_args__ = (
        UniqueConstraint(
            "document_id", "value",
            name="uq_documents_tags_document_id_value"
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

    value = Column(
        String(40),
        nullable=False,
        index=True
    )

    tag_document = relationship(
        "Document",
        back_populates="document_tags"
    )

    def __init__(self, document_id: int, value: str):
        self.document_id = document_id
        self.value = value
