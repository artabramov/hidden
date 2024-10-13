"""
This module defines a Pydantic model Comment which represents a comment
on a document. The model includes attributes for a unique identifier,
timestamps for creation and updates, user and document IDs, and the
comment's content.
"""

import time
from sqlalchemy import Column, BigInteger, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.config import get_config
from app.database import Base

cfg = get_config()


class Comment(Base):
    """
    A Pydantic model representing a comment on a document, including an
    optional unique identifier, timestamps for creation and last update,
    the IDs of the user and the document, and the content.
    """
    __tablename__ = "comments"
    _cacheable = True

    id = Column(BigInteger, primary_key=True)
    created_date = Column(Integer, index=True,
                          default=lambda: int(time.time()))
    updated_date = Column(Integer, index=True,
                          onupdate=lambda: int(time.time()), default=0)
    user_id = Column(BigInteger, ForeignKey("users.id"), index=True)
    document_id = Column(BigInteger, ForeignKey("documents.id"), index=True)
    comment_content = Column(String(512), nullable=False, index=True)

    comment_user = relationship(
        "User", back_populates="user_comments", lazy="joined")

    comment_document = relationship(
        "Document", back_populates="document_comments", lazy="joined")

    def __init__(self, user_id: int, document_id: int, comment_content: str):
        self.user_id = user_id
        self.document_id = document_id
        self.comment_content = comment_content

    @property
    def is_locked(self) -> bool:
        return self.comment_document.is_locked

    def to_dict(self):
        """
        Converts the Pydantic model instance into a dictionary with
        attribute names as keys and their values, useful for
        serialization or integration with APIs.
        """
        return {
            "id": self.id,
            "created_date": self.created_date,
            "updated_date": self.updated_date,
            "user_id": self.user_id,
            "document_id": self.document_id,
            "comment_content": self.comment_content,
            "comment_user": self.comment_user.to_dict(),
        }
