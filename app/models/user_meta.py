"""
Key-value metadata for users with audit timestamps.
One row per (user_id, meta_key).
"""

import time
from sqlalchemy import (
    Column, Integer, BigInteger, String, ForeignKey, UniqueConstraint
)
from sqlalchemy.orm import relationship
from app.sqlite import Base


class UserMeta(Base):
    __tablename__ = "users_meta"
    __table_args__ = (
        UniqueConstraint("user_id", "meta_key", name="uq_users_meta_user_key"),
        {"sqlite_autoincrement": True},
    )

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
        String(80),
        nullable=False,
        index=True
    )
    
    meta_value = Column(
        String(4096),
        nullable=True
    )

    meta_user = relationship(
        "User",
        back_populates="user_meta"
    )
