"""SQLAlchemy model for user metadata."""

import time
from sqlalchemy import (
    Column, Integer, BigInteger, String, ForeignKey, UniqueConstraint
)
from sqlalchemy.orm import relationship
from app.sqlite import Base


class UserMeta(Base):
    """
    SQLAlchemy model for user metadata. Stores a key-value pair
    linked to a user; keys are unique within each collection.
    """

    __tablename__ = "users_meta"
    __table_args__ = (
        UniqueConstraint(
            "user_id", "meta_key",
            name="uq_users_meta_user_id_meta_key"
        ),
        {"sqlite_autoincrement": True},
    )
    _cacheable = False

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
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

    meta_user = relationship(
        "User",
        back_populates="user_meta"
    )
