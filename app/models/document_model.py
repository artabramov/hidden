"""
The module defines an SQLAlchemy model for documents. It describes the
structure of the document entity, including its fields and relationships
with other entities such as users, collections, partners, and related
entities like tags, revisions, comments, downloads.
"""

import time
from sqlalchemy import Column, Integer, String, BigInteger, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.database import Base
from app.config import get_config
from app.helpers.encryption_helper import encrypt_value, decrypt_value

cfg = get_config()


class Document(Base):
    """
    SQLAlchemy model defines the document's metadata, including its
    filename, size, associated user and collection, and relationships
    to other entities like partners, revisions, tags, comments,
    downloads. It also handles the encryption of thumbnail filenames
    and provides various properties to retrieve related data.
    """
    __tablename__ = "documents"
    _cacheable = True

    id = Column(BigInteger, primary_key=True)
    created_date = Column(
        Integer, index=True, default=lambda: int(time.time()))
    updated_date = Column(
        Integer, index=True, onupdate=lambda: int(time.time()), default=0)
    user_id = Column(
        BigInteger, ForeignKey("users.id"), index=True, nullable=False)
    collection_id = Column(
        BigInteger, ForeignKey("collections.id"), index=True, nullable=False)
    partner_id = Column(
        BigInteger, ForeignKey("partners.id", ondelete="SET NULL"), index=True,
        nullable=True)
    latest_revision_id = Column(BigInteger, index=True, nullable=True)
    is_flagged = Column(Boolean, index=True)
    document_filename = Column(String(256), nullable=True)
    document_size = Column(BigInteger, index=True, nullable=False)
    document_mimetype = Column(String(256), index=True, nullable=True)
    document_summary = Column(String(512), nullable=True)
    thumbnail_filename_encrypted = Column(
        String(256), nullable=True, unique=True)
    revisions_count = Column(Integer, default=0)
    comments_count = Column(Integer, default=0)
    downloads_count = Column(Integer, default=0)

    document_user = relationship(
        "User", back_populates="user_documents", lazy="joined")

    document_collection = relationship(
        "Collection", back_populates="collection_documents", lazy="joined")

    document_partner = relationship(
        "Partner", back_populates="partner_documents", lazy="joined")

    document_tags = relationship(
        "Tag", back_populates="tag_document", lazy="joined",
        cascade="all, delete-orphan")

    document_revisions = relationship(
        "Revision", back_populates="revision_document",
        cascade="all, delete-orphan")

    document_comments = relationship(
        "Comment", back_populates="comment_document",
        cascade="all, delete-orphan")

    document_downloads = relationship(
        "Download", back_populates="download_document",
        cascade="all, delete-orphan")

    def __init__(self, user_id: int, collection_id: int,
                 document_filename: str, document_size: int = 0,
                 is_flagged: bool = False, document_mimetype: str = None,
                 document_summary: str = None, thumbnail_filename: str = None):
        """
        Initializes a new document instance. Sets the user ID,
        collection ID, filename, size, MIME type, summary, and
        optionally the thumbnail filename.
        """
        self.user_id = user_id
        self.collection_id = collection_id
        self.is_flagged = is_flagged
        self.document_filename = document_filename
        self.document_size = document_size
        self.documene_mimetype = document_mimetype
        self.document_summary = document_summary
        self.thumbnail_filename = thumbnail_filename

    @property
    def thumbnail_filename(self) -> str:
        """
        Retrieves the decrypted thumbnail filename.
        """
        return (decrypt_value(self.thumbnail_filename_encrypted)
                if self.thumbnail_filename_encrypted else None)

    @thumbnail_filename.setter
    def thumbnail_filename(self, value: str):
        """
        Sets the encrypted thumbnail filename.
        """
        self.thumbnail_filename_encrypted = (
            encrypt_value(value) if value else None)

    @property
    def is_locked(self) -> bool:
        """
        Determines if the document is locked based on the associated
        collection.
        """
        return (self.collection_id is not None and
                self.document_collection.is_locked)

    @property
    def thumbnail_url(self):
        """
        Constructs and returns the full URL for the document's thumbnail.
        """
        if self.thumbnail_filename:
            return cfg.THUMBNAILS_BASE_URL + self.thumbnail_filename

    @property
    def tag_values(self) -> list:
        """
        Returns a list of tag values associated with the document.
        """
        if self.document_tags:
            return [x.tag_value for x in self.document_tags]
        return []

    async def to_dict(self):
        """
        Converts the document instance into a dictionary representation,
        including all relevant metadata about the document.
        """
        return {
            "id": self.id,
            "created_date": self.created_date,
            "updated_date": self.updated_date,
            "user_id": self.user_id,
            "user_name": self.document_user.full_name,
            "collection_id": self.collection_id,
            "collection_name": self.document_collection.collection_name,
            "partner_id": self.partner_id,
            "partner_name": (self.document_partner.partner_name
                             if self.partner_id else None),
            "latest_revision_id": self.latest_revision_id,
            "is_flagged": self.is_flagged,
            "document_filename": self.document_filename,
            "document_size": self.document_size,
            "document_mimetype": self.document_mimetype,
            "document_summary": self.document_summary,
            "thumbnail_url": self.thumbnail_url,
            "document_tags": self.tag_values,

            "comments_count": self.comments_count,
            "downloads_count": self.downloads_count,
            "revisions_count": self.revisions_count,
        }
