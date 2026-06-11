# app/models/user.py
# SPDX-License-Identifier: GPL-3.0-only

import time
from enum import StrEnum

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Integer,
    SmallInteger,
    String,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class UserRole(StrEnum):
    READER = "reader"
    WRITER = "writer"
    EDITOR = "editor"
    ADMIN = "admin"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    created_at: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        index=True,
        default=lambda: int(time.time()),
    )

    updated_at: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        onupdate=lambda: int(time.time()),
    )

    suspended_until: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    last_authenticated_at: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    role: Mapped[str] = mapped_column(
        String(16),
        nullable=False,
        server_default=text("'reader'"),
        index=True,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text("0"),
    )

    username: Mapped[str] = mapped_column(
        String(40),
        nullable=False,
        unique=True,
    )

    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    failed_password_attempts: Mapped[int] = mapped_column(
        SmallInteger,
        nullable=False,
        server_default=text("0"),
    )

    password_verified_at: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    mfa_session_uuid: Mapped[str | None] = mapped_column(
        String(80),
        nullable=True,
        unique=True,
    )

    totp_secret_encrypted: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    failed_totp_attempts: Mapped[int] = mapped_column(
        SmallInteger,
        nullable=False,
        server_default=text("0"),
    )

    recovery_code_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    failed_recovery_code_attempts: Mapped[int] = mapped_column(
        SmallInteger,
        nullable=False,
        server_default=text("0"),
    )

    current_jti_encrypted: Mapped[str] = mapped_column(
        String(255),
        nullable=True,
    )

    display_name: Mapped[str] = mapped_column(
        String(40),
        nullable=False,
        index=True,
    )

    summary: Mapped[str | None] = mapped_column(
        String(4096),
        nullable=True,
    )

    @property
    def can_read(self) -> bool:
        return self.role in {
            UserRole.READER.value,
            UserRole.WRITER.value,
            UserRole.EDITOR.value,
            UserRole.ADMIN.value
        }

    @property
    def can_write(self) -> bool:
        return self.role in {
            UserRole.WRITER.value,
            UserRole.EDITOR.value,
            UserRole.ADMIN.value
        }

    @property
    def can_edit(self) -> bool:
        return self.role in {
            UserRole.EDITOR.value,
            UserRole.ADMIN.value
        }

    @property
    def can_admin(self) -> bool:
        return self.role in {
            UserRole.ADMIN.value
        }

    __table_args__ = (
        CheckConstraint(
            "role IN ('reader', 'writer', 'editor', 'admin')",
            name="ck_users_role",
        ),
        {"sqlite_autoincrement": True},
    )
