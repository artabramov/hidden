"""
Defines the SQLAlchemy ORM mapping for application users, including
available roles and the User entity with authentication data, access
role, status flags, timestamps, MFA fields, and optional profile
information; designed for SQLite with AUTOINCREMENT primary key but
portable across databases.
"""


import time
from sqlalchemy import (
    Column, BigInteger, SmallInteger, String, Boolean, Integer)
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property
from app.sqlite import Base
from app.models.user_meta import UserMeta  # noqa: F401
from app.models.user_thumbnail import UserThumbnail  # noqa: F401


class UserRole:
    """
    Defines the available user roles in the system.
    Each role determines the scope of permissions.
    """
    reader = "reader"
    writer = "writer"
    editor = "editor"
    admin = "admin"


class User(Base):
    """
    SQLAlchemy model for application users, representing authentication
    credentials, access role, status flags, audit timestamps, MFA fields,
    and optional profile information.
    """
    __tablename__ = "users"
    __table_args__ = {"sqlite_autoincrement": True}
    _cacheable = True

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True
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

    suspended_until_date = Column(
        BigInteger,
        nullable=False,
        default=0
    )

    last_login_date = Column(
        BigInteger,
        nullable=False,
        default=0
    )

    role = Column(
        String(8),
        nullable=False,
        index=True
    )

    active = Column(
        Boolean,
        nullable=False,
    )

    username = Column(
        String(40),
        nullable=False,
        unique=True
    )

    password_hash = Column(
        String(128),
        nullable=False
    )

    password_attempts = Column(
        SmallInteger,
        nullable=False,
        default=0
    )

    password_accepted = Column(
        Boolean,
        nullable=False,
        default=False
    )

    mfa_secret_encrypted = Column(
        String(128),
        nullable=False
    )

    mfa_attempts = Column(
        SmallInteger,
        nullable=False,
        default=0
    )

    jti_encrypted = Column(
        String(128),
        nullable=False
    )

    first_name = Column(
        String(40),
        nullable=False,
        index=True,
    )

    last_name = Column(
        String(40),
        nullable=False,
        index=True,
    )

    summary = Column(
        String(4096),
        nullable=True
    )

    @hybrid_property
    def full_name(self) -> str:
        return self.first_name + " " + self.last_name

    user_meta = relationship(
        "UserMeta",
        back_populates="meta_user",
        cascade="all, delete-orphan",
        lazy="selectin",
        passive_deletes=True
    )

    user_thumbnail = relationship(
        "UserThumbnail",
        back_populates="thumbnail_user",
        cascade="all, delete-orphan",
        uselist=False,
        lazy="joined"
    )
        
    def __init__(
            self, username: str, password_hash: str, first_name: str,
            last_name: str, role: UserRole, active: bool,
            mfa_secret_encrypted: str, jti_encrypted: str, 
            summary: str = None):

        self.role = role
        self.active = active
        self.username = username
        self.password_hash = password_hash
        self.password_accepted = False
        self.mfa_secret_encrypted = mfa_secret_encrypted
        self.jti_encrypted = jti_encrypted
        self.first_name = first_name
        self.last_name = last_name
        self.summary = summary

    @property
    def can_read(self) -> bool:
        return self.role in [UserRole.admin, UserRole.editor,
                             UserRole.writer, UserRole.reader]

    @property
    def can_write(self) -> bool:
        return self.role in [UserRole.admin, UserRole.editor,
                             UserRole.writer]

    @property
    def can_edit(self) -> bool:
        return self.role in [UserRole.admin, UserRole.editor]

    @property
    def can_admin(self) -> bool:
        return self.role == UserRole.admin

    @property
    def has_thumbnail(self) -> bool:
        return self.user_thumbnail is not None

    async def to_dict(self) -> dict:
        return {
            "id": self.id,
            "created_date": self.created_date,
            "last_login_date": self.last_login_date,
            "role": self.role,
            "active": self.active,
            "username": self.username,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "summary": self.summary,
            "has_thumbnail": self.has_thumbnail,
        }
