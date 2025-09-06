"""
SQLAlchemy model for a collection of documents.

Stores basic metadata (name, summary) and Unix timestamps (seconds)
for creation and last update times.
"""

import time
from typing import Optional

from sqlalchemy import Boolean, Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from app.sqlite import Base


class Collection(Base):
    __tablename__ = "collections"
    _cacheable = True

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    created_date: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=lambda: int(time.time()),
    )

    updated_date: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=lambda: int(time.time()),
        onupdate=lambda: int(time.time()),
    )

    readonly: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
    )

    private: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
    )

    collection_name: Mapped[str] = mapped_column(
        String(256),
        nullable=False,
        unique=True,
    )

    collection_summary: Mapped[Optional[str]] = mapped_column(
        String(2048),
        nullable=True,
    )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "created_date": self.created_date,
            "updated_date": self.updated_date,
            "collection_name": self.collection_name,
            "collection_summary": self.collection_summary,
        }
