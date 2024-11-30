"""
The module defines a SQLAlchemy model representing a download entity.
It tracks the details of document downloads, including the associated
user, document, and revision. The model also includes relationships
to other entities such as users, documents, and revisions.
"""

from sqlalchemy import Column, BigInteger, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.config import get_config
from app.database import Base
import time

cfg = get_config()


class Download(Base):
    """
    SQLAlchemy model representing a download entity. It stores
    information about downloads of documents and their revisions by
    users. The model tracks the user who initiated the download, the
    document being downloaded, and the specific revision of the
    document, as well as providing relationships to related entities
    such as users, documents, and revisions.
    """
    __tablename__ = "documents_downloads"
    _cacheable = True

    id = Column(BigInteger, primary_key=True)
    created_date = Column(Integer, index=True,
                          default=lambda: int(time.time()))
    user_id = Column(BigInteger, ForeignKey("users.id"), index=True)
    document_id = Column(BigInteger, ForeignKey("documents.id"), index=True)
    revision_id = Column(BigInteger, ForeignKey("documents_revisions.id"),
                         index=True)

    download_user = relationship(
        "User", back_populates="user_downloads", lazy="joined")

    download_document = relationship(
        "Document", back_populates="document_downloads", lazy="joined")

    download_revision = relationship(
        "Revision", back_populates="revision_downloads", lazy="joined")

    def __init__(self, user_id: int, document_id: int, revision_id: int):
        """
        Initializes a new download instance. Sets the user ID, document
        ID, and revision ID associated with the download.
        """
        self.user_id = user_id
        self.document_id = document_id
        self.revision_id = revision_id

    async def to_dict(self):
        """
        Converts the download instance to a dictionary. The dictionary
        includes attributes such as the download ID, creation date,
        user ID and name, document ID, document filename, and
        revision ID.
        """
        return {
            "id": self.id,
            "created_date": self.created_date,
            "user_id": self.user_id,
            "user_name": self.download_user.full_name,
            "document_id": self.document_id,
            "document_filename": self.download_document.document_filename,
            "revision_id": self.revision_id,
        }
