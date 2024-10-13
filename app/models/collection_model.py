"""
Represents a collection of documents in the database. Manages data
about the collection, including its name, summary, and the count and
size of documents within it. Handles relationships with users and
documents through SQLAlchemy, providing attributes for creation and
modification timestamps, user association, and document statistics.
Includes a method to convert the collection instance to a dictionary.
"""

import time
from sqlalchemy.orm import relationship
from sqlalchemy import (Boolean, Column, BigInteger, Integer, ForeignKey,
                        String)
from app.config import get_config
from app.database import Base

cfg = get_config()


class Collection(Base):
    """
    SQLAlchemy model for a document collection. Defines a collection
    of documents with metadata such as creation and update dates, user
    association, and collection details including name, summary, and
    document statistics. Manages relationships with users and
    documents.
    """

    __tablename__ = "collections"
    _cacheable = True

    id = Column(BigInteger, primary_key=True)
    created_date = Column(
        Integer, index=True, default=lambda: int(time.time()))
    updated_date = Column(
        Integer, index=True, onupdate=lambda: int(time.time()), default=0)
    user_id = Column(BigInteger, ForeignKey("users.id"), index=True)
    is_locked = Column(Boolean, index=True)
    collection_name = Column(String(256), index=True, unique=True)
    collection_summary = Column(String(512), nullable=True)
    documents_count = Column(Integer, index=True, default=0)

    collection_user = relationship(
        "User", back_populates="user_collections", lazy="joined")

    collection_documents = relationship(
        "Document", back_populates="document_collection",
        cascade="all, delete-orphan")

    def __init__(self, user_id: int, is_locked: bool, collection_name: str,
                 collection_summary: str = None):
        """
        Initializes a new Collection instance with the specified user
        ID, lock status, collection name, and optional summary. Sets the
        initial document count and size to zero.
        """
        self.user_id = user_id
        self.is_locked = is_locked
        self.collection_name = collection_name
        self.collection_summary = collection_summary
        self.documents_count = 0

    def to_dict(self):
        """
        Converts the Collection instance into a dictionary
        representation, including all its attributes and related
        objects. The resulting dictionary includes fields such as ID,
        creation and update dates, user ID, lock status, collection
        name, summary, documents count, documents size, and details
        of the associated user.
        """
        return {
            "id": self.id,
            "created_date": self.created_date,
            "updated_date": self.updated_date,
            "user_id": self.user_id,
            "is_locked": self.is_locked,
            "collection_name": self.collection_name,
            "collection_summary": self.collection_summary,
            "documents_count": self.documents_count,
            "collection_user": self.collection_user.to_dict(),
        }
