"""SQLAlchemy model for collection metadata."""

import time
from sqlalchemy import (
    Column, Integer, BigInteger, String, ForeignKey, UniqueConstraint
)
from sqlalchemy.orm import relationship
from app.sqlite import Base


class CollectionMeta(Base):
    """
    SQLAlchemy model for collection metadata. Stores a key-value pair
    linked to a collection; keys are unique within each collection.
    """

    __tablename__ = "collections_meta"
    __table_args__ = (
        UniqueConstraint(
            "collection_id", "meta_key",
            name="uq_collections_meta_collection_id_meta_key"
        ),
        {"sqlite_autoincrement": True},
    )

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    collection_id = Column(
        Integer,
        ForeignKey("collections.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    created_date = Column(
        BigInteger,
        nullable=False,
        index=True,
        default=lambda: int(time.time())
    )

    updated_date = Column(
        BigInteger,
        nullable=False,
        index=True,
        default=lambda: int(time.time()),
        onupdate=lambda: int(time.time())
    )

    meta_key = Column(
        String(128),
        nullable=False
    )
    
    meta_value = Column(
        String(4096),
        nullable=True
    )

    meta_collection = relationship(
        "Collection",
        back_populates="collection_meta"
    )
