"""SQLAlchemy model for collections."""

import time
from sqlalchemy import Column, BigInteger, String, Boolean, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.sqlite import Base
from app.models.collection_meta import CollectionMeta  # noqa: F401


class Collection(Base):
    """
    SQLAlchemy model for collections. Stores a unique name, read-only
    flag, creation/update timestamps, and optional summary.
    """
    __tablename__ = "collections"
    _cacheable = True

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
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

    readonly = Column(
        Boolean,
        nullable=False,
    )

    name = Column(
        String(256),
        nullable=False,
        unique=True
    )

    summary = Column(
        String(4096),
        nullable=True
    )

    collection_meta = relationship(
        "CollectionMeta",
        back_populates="meta_collection",
        cascade="all, delete-orphan",
        lazy="selectin",
        passive_deletes=True
    )

    collection_user = relationship(
        "User",
        back_populates="user_collections",
        lazy="joined"
    )

    collection_documents = relationship(
        "Document",
        back_populates="document_collection",
        lazy="noload"
    )

    def __init__(self, user_id: int, name: str, readonly: bool = False,
                 summary: str = None):
        self.user_id = user_id
        self.name = name
        self.readonly = readonly
        self.summary = summary

    async def to_dict(self) -> dict:
        """Returns a dictionary representation of the collection."""
        return {
            "id": self.id,
            "user": await self.collection_user.to_dict(),
            "created_date": self.created_date,
            "updated_date": self.updated_date,
            "readonly": self.readonly,
            "name": self.name,
            "summary": self.summary,
        }
