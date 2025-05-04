"""
The module defines the SQLAlchemy model for managing collection metadata.
It includes encryption and decryption for sensitive data fields, supports
a relationship with the collections table, and provides properties for
handling metadata attributes.
"""

import time
from sqlalchemy import Column, BigInteger, String, ForeignKey
from sqlalchemy.orm import relationship
from app.config import get_config
from app.postgres import Base
from app.helpers.encrypt_helper import (
    encrypt_int, decrypt_int, encrypt_str, decrypt_str, hash_str)

cfg = get_config()


class CollectionMeta(Base):
    """
    An SQLAlchemy model representing metadata for collections. The model
    supports encryption for sensitive data such as creation and update
    timestamps, as well as metadata keys and values. It also establishes
    a relationship with the collection model, enabling access to the
    collection associated with the metadata.
    """
    __tablename__ = "collections_meta"
    _cacheable = False

    id = Column(BigInteger, primary_key=True)

    # original length up to 15
    created_date_encrypted = Column(
        String(64), nullable=False,
        default=lambda: encrypt_int(int(time.time())))

    # original length up to 15
    updated_date_encrypted = Column(
        String(64), nullable=False, default=lambda: encrypt_int(0),
        onupdate=lambda: encrypt_int(int(time.time())))

    collection_id = Column(
        BigInteger, ForeignKey("collections.id"),
        nullable=False, index=True)

    # value length up to 47
    meta_key_encrypted = Column(String(108), nullable=False)
    meta_key_hash = Column(String(128), nullable=False, index=True)

    # value length up to 511
    meta_value_encrypted = Column(String(728), nullable=True)

    meta_collection = relationship(
        "Collection", back_populates="collection_meta",
        lazy="noload")

    def __init__(self, collection_id: int, meta_key: str, meta_value: str):
        """
        Initializes a new instance of the collection metadata model. It
        accepts a collection ID, a metadata key, and a metadata value,
        which are used to set the corresponding attributes for this
        metadata entry.
        """
        self.collection_id = collection_id
        self.meta_key = meta_key
        self.meta_value = meta_value

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
    def meta_key(self):
        return decrypt_str(self.meta_key_encrypted)

    @meta_key.setter
    def meta_key(self, meta_key: str):
        self.meta_key_encrypted = encrypt_str(meta_key)
        self.meta_key_hash = hash_str(meta_key)

    @property
    def meta_value(self):
        return decrypt_str(self.meta_value_encrypted)

    @meta_value.setter
    def meta_value(self, meta_value: str):
        self.meta_value_encrypted = encrypt_str(meta_value)
