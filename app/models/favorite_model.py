"""
This module defines the Favorite model for managing user favorites of
documents in the database. The Favorite class includes fields for
tracking the user who favorited a document, the document itself, and
the date when the favorite was created. It also establishes
relationships with User and document models and provides methods
to initialize instances and convert them to dictionaries.
"""

import time
from sqlalchemy import Column, BigInteger, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.config import get_config
from app.database import Base

cfg = get_config()


class Favorite(Base):
    """
    Represents a user's favorite document. Each favorite is linked to a
    specific user and document, and includes a creation timestamp.
    """
    __tablename__ = "favorites"
    _cacheable = False

    id = Column(BigInteger, primary_key=True)
    created_date = Column(Integer, index=True,
                          default=lambda: int(time.time()))
    user_id = Column(BigInteger, ForeignKey("users.id"), index=True)
    document_id = Column(BigInteger, ForeignKey("documents.id"), index=True)

    favorite_user = relationship(
        "User", back_populates="user_favorites", lazy="noload")

    favorite_document = relationship(
        "Document", back_populates="document_favorites", lazy="joined")

    def __init__(self, user_id: int, document_id: int):
        """
        Initializes a Favorite instance with the specified user_id
        and document_id.
        """
        self.user_id = user_id
        self.document_id = document_id

    def to_dict(self):
        """
        Converts the Favorite instance to a dictionary, including
        related user and document details.
        """
        return {
            "id": self.id,
            "created_date": self.created_date,
            "user_id": self.user_id,
            "document_id": self.document_id,
            "favorite_document": self.favorite_document.to_dict(),
        }
