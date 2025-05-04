"""
The module defines the SQLAlchemy model for the collection entity, which
represents a collection of documents. The model includes metadata
management, relationships with user and document entities, and handles
encrypted attributes such as collection name, summary, and timestamps.
It also supports functionalities for managing the collection's thumbnail
and related metadata.
"""

import os
import time
from typing import Union
from sqlalchemy.orm import relationship
from sqlalchemy import Column, BigInteger, ForeignKey, String
from app.postgres import Base
from app.mixins.meta_mixin import MetaMixin
from app.models.collection_meta_model import CollectionMeta
from app.helpers.encrypt_helper import (
    encrypt_int, decrypt_int, encrypt_str, decrypt_str, hash_str)
from app.helpers.sort_helper import get_index
from app.config import get_config

cfg = get_config()


class Collection(Base, MetaMixin):
    """
    An SQLAlchemy model representing a collection entity. The model
    defines the structure of a collection. It includes data about the
    collection, such as creation and update dates, a collection name,
    a collection summary, and an optional thumbnail image. The model
    manages relationships with the user who created the collection and
    the documents that belong to it. It also provides methods for
    encrypting and decrypting sensitive data such as collection names
    and summaries.
    """
    __tablename__ = "collections"
    _cacheable = True
    _meta = CollectionMeta

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
        BigInteger, ForeignKey("users.id"), index=True, nullable=False)

    # value length up to 79
    collection_name_encrypted = Column(String(152), nullable=False)
    collection_name_hash = Column(String(128), nullable=False, index=True)
    collection_name_index = Column(BigInteger, nullable=False, index=True)

    # value length up to 4095
    collection_summary_encrypted = Column(String(5504), nullable=True)

    # original length up to 79
    thumbnail_filename_encrypted = Column(String(152), nullable=True)

    collection_user = relationship(
        "User", back_populates="user_collections", lazy="joined")

    collection_documents = relationship(
        "Document", back_populates="document_collection",
        cascade="all, delete-orphan")

    collection_meta = relationship(
        "CollectionMeta", back_populates="meta_collection", lazy="joined",
        cascade="all, delete-orphan")

    def __init__(self, user_id: int, collection_name: str,
                 collection_summary: str = None):
        self.user_id = user_id
        self.collection_name = collection_name
        self.collection_summary = collection_summary
        self.thumbnail_filename = None

    @property
    def created_date(self) -> int:
        return decrypt_int(self.created_date_encrypted)

    @property
    def updated_date(self) -> int:
        return decrypt_int(self.updated_date_encrypted)

    @updated_date.setter
    def updated_date(self, updated_date: int):
        self.updated_date_encrypted = encrypt_int(updated_date)

    @property
    def collection_name(self):
        return decrypt_str(self.collection_name_encrypted)

    @collection_name.setter
    def collection_name(self, collection_name: str):
        self.collection_name_encrypted = encrypt_str(collection_name)
        self.collection_name_hash = hash_str(collection_name)
        self.collection_name_index = get_index(collection_name)

    @property
    def collection_summary(self) -> Union[str, None]:
        return decrypt_str(self.collection_summary_encrypted)

    @collection_summary.setter
    def collection_summary(self, collection_summary: str):
        self.collection_summary_encrypted = encrypt_str(collection_summary)

    @property
    def thumbnail_filename(self) -> Union[str, None]:
        return decrypt_str(self.thumbnail_filename_encrypted)

    @thumbnail_filename.setter
    def thumbnail_filename(self, thumbnail_filename: str):
        self.thumbnail_filename_encrypted = encrypt_str(thumbnail_filename)

    @property
    def thumbnail_url(self):
        if self.has_thumbnail:
            return cfg.USERPICS_URL + self.thumbnail_filename

    @property
    def thumbnail_path(self):
        if self.has_thumbnail:
            return os.path.join(cfg.USERPICS_PATH, self.thumbnail_filename)

    @property
    def has_thumbnail(self):
        return self.thumbnail_filename is not None

    async def to_dict(self):
        return {
            "id": self.id,
            "created_date": self.created_date,
            "updated_date": self.updated_date,
            "user_id": self.user_id,
            "username": self.collection_user.username,
            "collection_name": self.collection_name,
            "collection_summary": self.collection_summary,
            "thumbnail_url": self.thumbnail_url,
            "collection_meta": {
                meta.meta_key: meta.meta_value
                for meta in self.collection_meta},
        }
