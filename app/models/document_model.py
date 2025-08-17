"""
The module defines the SQLAlchemy model for documents. The model
represents a document and its associated metadata, including the
original filename, size, MIME type, and summary. It supports
relationships with collections, users, tags, and document metadata.
The module also provides methods for handling encryption,
generating URLs, and deleting associated files.
"""

import os
import time
import asyncio
from typing import Union
from sqlalchemy import Column, String, BigInteger, ForeignKey, event
from sqlalchemy.orm import relationship
from app.postgres import Base
from app.config import get_config
from app.helpers.encrypt_helper import (
    encrypt_str, decrypt_str, encrypt_int, decrypt_int)
from app.helpers.sort_helper import get_index
from app.managers.file_manager import FileManager
from app.models.document_meta_model import DocumentMeta
from app.mixins.meta_mixin import MetaMixin
from app.log import get_log

cfg = get_config()
log = get_log()


class Document(Base, MetaMixin):
    """
    Represents an SQLAlchemy model within the app. It stores information
    about the document, such as its original filename, size, MIME type,
    and summary. The class supports encryption and decryption of
    sensitive data and facilitates relationships with other entities
    such as users, collections, tags, and document metadata.
    """
    __tablename__ = "documents"
    _cacheable = True
    _meta = DocumentMeta

    id = Column(BigInteger, primary_key=True)

    # original length up to 15
    created_date_encrypted = Column(
        String(64), nullable=False,
        default=lambda: encrypt_int(int(time.time())))

    # original length up to 15
    updated_date_encrypted = Column(
        String(64), nullable=False, default=lambda: encrypt_int(0),
        onupdate=lambda: encrypt_int(int(time.time())))

    user_id = Column(
        BigInteger, ForeignKey("users.id"),
        index=True, nullable=False)

    collection_id = Column(
        BigInteger, ForeignKey("collections.id"),
        index=True, nullable=True)

    # value length up to 255
    original_filename_encrypted = Column(String(384), nullable=False)
    original_filename_index = Column(BigInteger, nullable=False, index=True)

    # value length up to 15
    document_filesize_encrypted = Column(String(64), nullable=False)
    document_filesize_index = Column(BigInteger, nullable=False, index=True)

    # value length up to 255
    document_mimetype_encrypted = Column(String(384), nullable=False)
    document_mimetype_index = Column(BigInteger, nullable=False, index=True)

    # value length up to 4095
    document_summary_encrypted = Column(String(5504), nullable=True)

    # original length up to 79
    thumbnail_filename_encrypted = Column(String(152), nullable=True)

    document_user = relationship(
        "User", back_populates="user_documents", lazy="joined")

    document_collection = relationship(
        "Collection", back_populates="collection_documents", lazy="joined")

    document_tags = relationship(
        "Tag", back_populates="tag_document", lazy="joined",
        cascade="all, delete-orphan")

    document_shards = relationship(
        "Shard", back_populates="shard_document", lazy="joined",
        cascade="all, delete-orphan")

    document_meta = relationship(
        "DocumentMeta", back_populates="meta_document", lazy="joined",
        cascade="all, delete-orphan")

    def __init__(self, user_id: int, original_filename: str,
                 document_filename: str, document_filesize: int,
                 document_mimetype: str, collection_id: int = None,
                 document_summary: str = None, thumbnail_filename: str = None):
        """
        Initializes a new document instance. This constructor accepts
        parameters for user ID, original filename, document filesize,
        document mimetype, collection ID, document summary, and
        thumbnail filename. These attributes are used to set the
        corresponding fields for the document.
        """
        self.user_id = user_id
        self.collection_id = collection_id
        self.original_filename = original_filename
        self.document_filesize = document_filesize
        self.document_mimetype = document_mimetype
        self.document_summary = document_summary
        self.thumbnail_filename = thumbnail_filename
        self.document_meta = []

    @property
    def created_date(self):
        return decrypt_int(self.created_date_encrypted)

    @property
    def updated_date(self) -> int:
        return decrypt_int(self.updated_date_encrypted)

    @updated_date.setter
    def updated_date(self, updated_date: int):
        self.updated_date_encrypted = encrypt_int(updated_date)

    @property
    def original_filename(self):
        return decrypt_str(self.original_filename_encrypted)

    @original_filename.setter
    def original_filename(self, original_filename: str):
        self.original_filename_encrypted = encrypt_str(original_filename)
        self.original_filename_index = get_index(original_filename)

    @property
    def document_filesize(self):
        return decrypt_int(self.document_filesize_encrypted)

    @document_filesize.setter
    def document_filesize(self, document_filesize: int):
        self.document_filesize_encrypted = encrypt_int(document_filesize)
        self.document_filesize_index = get_index(document_filesize)

    @property
    def document_mimetype(self):
        return decrypt_str(self.document_mimetype_encrypted)

    @document_mimetype.setter
    def document_mimetype(self, document_mimetype: str):
        self.document_mimetype_encrypted = encrypt_str(document_mimetype)
        self.document_mimetype_index = get_index(document_mimetype)

    @property
    def document_summary(self) -> Union[str, None]:
        return decrypt_str(self.document_summary_encrypted)

    @document_summary.setter
    def document_summary(self, document_summary: str):
        self.document_summary_encrypted = encrypt_str(document_summary)

    @property
    def thumbnail_filename(self):
        return decrypt_str(self.thumbnail_filename_encrypted)

    @thumbnail_filename.setter
    def thumbnail_filename(self, thumbnail_filename: str):
        self.thumbnail_filename_encrypted = encrypt_str(thumbnail_filename)

    @property
    def collection_name(self):
        return (self.document_collection.collection_name
                if self.collection_id else None)

    @property
    def has_thumbnail(self):
        return self.thumbnail_filename_encrypted is not None

    @property
    def document_path(self):
        return os.path.join(cfg.DOCUMENTS_PATH, str(self.id))

    @property
    def thumbnail_path(self):
        if self.has_thumbnail:
            return os.path.join(cfg.THUMBNAILS_PATH, self.thumbnail_filename)

    async def to_dict(self):
        return {
            "id": self.id,
            "created_date": self.created_date,
            "updated_date": self.updated_date,
            "user_id": self.user_id,
            "username": self.document_user.username,
            "collection_id": self.collection_id,
            "collection_name": self.collection_name,
            "original_filename": self.original_filename,
            "document_filesize": self.document_filesize,
            "document_mimetype": self.document_mimetype,
            "document_summary": self.document_summary,
            "thumbnail_filename": self.thumbnail_filename,
            "document_tags": [
                x.tag_value for x in self.document_tags],
            "document_meta": {
                meta.meta_key: meta.meta_value
                for meta in self.document_meta},
        }


@event.listens_for(Document, "after_delete")
def after_delete_document(mapper, connection, document: Document):
    """
    Event listener triggered after a document is deleted. It
    executes asyncio tasks to delete the the thumbnail file.
    """
    if document.has_thumbnail:
        asyncio.get_event_loop().create_task(delete_file(document))


async def delete_file(document: Document):
    """Deletes the thumbnail file."""
    try:
        await FileManager.delete(document.thumbnail_path)
    except Exception as e:
        log.error("File deletion failed; module=document_model; "
                  "function=delete_file; e=%s;" % str(e))
