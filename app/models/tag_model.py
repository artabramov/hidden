"""
The module defines the SQLAlchemy model for associating tags with
documents in the database. The model supports the relationship with
documents.
"""

import time
from sqlalchemy import Column, BigInteger, String, ForeignKey
from sqlalchemy.orm import relationship
from app.config import get_config
from app.postgres import Base
from app.helpers.encrypt_helper import (
    encrypt_int, decrypt_int, encrypt_str, decrypt_str, hash_str)

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

    # original length up to 15
    created_date_encrypted = Column(
        String(64), nullable=False,
        default=lambda: encrypt_int(int(time.time())))

    document_id = Column(BigInteger, ForeignKey("documents.id"),
                         nullable=False, index=True)

    # value length up to 47
    tag_value_encrypted = Column(String(108), nullable=False)
    tag_value_hash = Column(String(128), nullable=False, index=True)

    tag_document = relationship("Document", back_populates="document_tags",
                                lazy="noload")

    def __init__(self, document_id: int, tag_value: str):
        """
        Initializes a new tag instance. This constructor accepts a
        document ID and a tag value, which are used to set the
        corresponding attributes for the tag.
        """
        self.document_id = document_id
        self.tag_value = tag_value

    @property
    def created_date(self):
        return decrypt_int(self.created_date_encrypted)

    @property
    def tag_value(self):
        return decrypt_str(self.tag_value_encrypted)

    @tag_value.setter
    def tag_value(self, tag_value: str):
        self.tag_value_encrypted = encrypt_str(tag_value)
        self.tag_value_hash = hash_str(tag_value)
