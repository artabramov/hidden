"""
The module defines an SQLAlchemy model for comments, which represent
user comments on documents. It defines the structure of the comment
entity and its relationships with users and documents.
"""

import time
from sqlalchemy import Column, BigInteger, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.config import get_config
from app.database import Base

cfg = get_config()


class Comment(Base):
    """
    SQLAlchemy model representing a comment.
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
        """
        Initializes a new comment instance.
        """
        self.user_id = user_id
        self.document_id = document_id
        self.comment_content = comment_content

    @property
    def is_locked(self) -> bool:
        """
        Determines if the associated document is locked.
        """
        return self.comment_document.is_locked

    async def to_dict(self):
        """
        Converts the comment instance into a dictionary representation.
        """
        return {
            "id": self.id,
            "created_date": self.created_date,
            "updated_date": self.updated_date,
            "user_id": self.user_id,
            "user_name": self.comment_user.full_name,
            "document_id": self.document_id,
            "comment_content": self.comment_content,
        }
