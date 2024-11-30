"""
The module defines a SQLAlchemy model representing a collection entity,
which defines the structure of the collection and its relationships to
other entities.
"""

import time
from sqlalchemy.orm import relationship
from sqlalchemy import Boolean, Column, BigInteger, Integer, ForeignKey, String
from app.database import Base


class Collection(Base):
    """
    SQLAlchemy model representing a collection entity. This model
    defines the structure of a collection, including its attributes
    such as the collection name, summary, and locked status. It manages
    relationships with other entities such as the user who creates the
    collection and the documents associated with the collection. The
    class also includes functionality to track the locking of the
    collection and the number of documents contained within it. It
    provides an asynchronous method for serializing the collection's
    data into a dictionary format.
    """
    __tablename__ = "collections"
    _cacheable = True

    id = Column(BigInteger, primary_key=True)
    created_date = Column(
        Integer, index=True, default=lambda: int(time.time()))
    updated_date = Column(
        Integer, index=True, onupdate=lambda: int(time.time()), default=0)
    locked_date = Column(Integer, nullable=False, default=0)
    user_id = Column(BigInteger, ForeignKey("users.id"), index=True)
    is_locked = Column(Boolean, index=True)
    collection_name = Column(String(256), index=True, unique=True)
    collection_summary = Column(String(512), nullable=True)
    documents_count = Column(Integer, default=0)

    collection_user = relationship(
        "User", back_populates="user_collections", lazy="joined")

    collection_documents = relationship(
        "Document", back_populates="document_collection",
        cascade="all, delete-orphan")

    def __init__(self, user_id: int, is_locked: bool, collection_name: str,
                 collection_summary: str = None):
        """
        Initializes a new collection instance. Sets the user ID, lock
        status, collection name, and an optional collection summary.
        The locked date is automatically set if the collection is locked.
        """
        self.user_id = user_id
        self.is_locked = is_locked
        self.locked_date = int(time.time()) if self.is_locked else 0
        self.collection_name = collection_name
        self.collection_summary = collection_summary

    async def to_dict(self):
        """
        Converts the collection instance to a dictionary. The dictionary
        contains various attributes of the collection such as its ID,
        creation and update dates, locked status, name, summary, and the
        count of associated documents.
        """
        return {
            "id": self.id,
            "created_date": self.created_date,
            "updated_date": self.updated_date,
            "locked_date": self.locked_date,
            "user_id": self.user_id,
            "user_name": self.collection_user.full_name,
            "is_locked": self.is_locked,
            "collection_name": self.collection_name,
            "collection_summary": self.collection_summary,
            "documents_count": self.documents_count,
        }
