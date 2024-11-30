"""
This module defines the Tag model for associating tags with documents in
the database. The Tag class includes fields for the tag value and the
associated document ID, and provides methods for initializing instances
of tags. The model supports the relationship with the Document model.
"""

import time
from sqlalchemy import Column, BigInteger, String, ForeignKey, Integer
from sqlalchemy.orm import relationship
from app.config import get_config
from app.database import Base

cfg = get_config()


class Tag(Base):
    """
    Represents a tag associated with a document. Each tag is linked to a
    specific document and contains a tag value. The class supports the
    relationship between documents and their associated tags, and
    provides methods for initializing tags for documents.
    """
    __tablename__ = "documents_tags"
    _cacheable = False

    id = Column(BigInteger, primary_key=True)
    created_date = Column(Integer, index=True,
                          default=lambda: int(time.time()))
    document_id = Column(BigInteger, ForeignKey("documents.id"),
                         nullable=False, index=True)
    tag_value = Column(String(256), nullable=False, index=True)

    tag_document = relationship("Document", back_populates="document_tags",
                                lazy="noload")

    def __init__(self, document_id: int, tag_value: str):
        """
        Initializes a new Tag instance. This constructor accepts a
        document ID and a tag value, which are used to set the
        corresponding attributes for the tag.
        """
        self.document_id = document_id
        self.tag_value = tag_value
