import os
import enum
import time
from sqlalchemy import (Boolean, Column, BigInteger, Integer, SmallInteger,
                        String, Enum)
from sqlalchemy.ext.hybrid import hybrid_property
from app.mixins.mfa_mixin import MFAMixin
from app.mixins.fernet_mixin import FernetMixin
from app.helpers.hash_helper import get_hash
from sqlalchemy.orm import relationship
from app.config import get_config
from app.database import Base
from app.helpers.jwt_helper import jti_create

cfg = get_config()


class UserRole(enum.Enum):
    reader = "reader"
    writer = "writer"
    editor = "editor"
    admin = "admin"


class User(Base, MFAMixin, FernetMixin):
    __tablename__ = "users"
    _cacheable = True

    id = Column(BigInteger, primary_key=True)
    created_date = Column(Integer, index=True,
                          default=lambda: int(time.time()))
    updated_date = Column(Integer, index=True, default=0,
                          onupdate=lambda: int(time.time()))
    last_login_date = Column(Integer, nullable=False, index=True, default=0)
    suspended_date = Column(Integer, nullable=False, default=0)
    user_role = Column(Enum(UserRole), nullable=False, index=True,
                       default=UserRole.reader)
    is_active = Column(Boolean, nullable=False, index=True)
    user_login = Column(String(40), nullable=False, index=True, unique=True)
    password_hash = Column(String(128), nullable=False, index=True)
    password_attempts = Column(SmallInteger, nullable=False, default=0)
    password_accepted = Column(Boolean, nullable=False, default=False)
    first_name = Column(String(40), nullable=False, index=True)
    last_name = Column(String(40), nullable=False, index=True)
    mfa_secret_encrypted = Column(String(256), nullable=False, unique=True)
    mfa_attempts = Column(SmallInteger(), nullable=False, default=0)
    jti_encrypted = Column(String(256), nullable=False, unique=True)
    user_signature = Column(String(40), index=False, nullable=True)
    user_contacts = Column(String(512), index=False, nullable=True)
    userpic_filename = Column(String(128), nullable=True, unique=True)

    user_collections = relationship(
        "Collection", back_populates="collection_user", lazy="noload")
    user_members = relationship(
        "Member", back_populates="member_user", lazy="noload")
    user_documents = relationship(
        "Document", back_populates="document_user", lazy="noload")
    user_revisions = relationship(
        "Revision", back_populates="revision_user", lazy="noload")
    user_comments = relationship(
        "Comment", back_populates="comment_user", lazy="noload")
    user_downloads = relationship(
        "Download", back_populates="download_user", lazy="noload")
    user_favorites = relationship(
        "Favorite", back_populates="favorite_user", lazy="noload")
    user_options = relationship(
        "Option", back_populates="option_user", lazy="noload")

    def __init__(self, user_role: UserRole, user_login: str,
                 user_password: str, first_name: str, last_name: str,
                 is_active: bool = False, user_signature: str = "",
                 user_contacts: str = ""):
        self.last_login_date = 0
        self.suspended_date = 0
        self.user_role = user_role
        self.is_active = is_active
        self.user_login = user_login
        self.password_hash = get_hash(user_password)
        self.password_attempts = 0
        self.password_accepted = False
        self.first_name = first_name
        self.last_name = last_name
        self.mfa_secret = self.create_mfa_secret()
        self.mfa_attempts = 0
        self.jti = jti_create()
        self.user_signature = user_signature
        self.user_contacts = user_contacts
        self.userpic_filename = None

    @property
    def mfa_secret(self) -> str:
        return self.decrypt(self.mfa_secret_encrypted)

    @mfa_secret.setter
    def mfa_secret(self, value: str):
        self.mfa_secret_encrypted = self.encrypt(value)

    @property
    def mfa_url(self):
        return cfg.APP_BASE_URL + cfg.APP_PREFIX + "/user/%s/mfa/%s" % (
            self.id, self.mfa_secret)

    @property
    def jti(self) -> str:
        return self.decrypt(self.jti_encrypted)

    @jti.setter
    def jti(self, value: str):
        self.jti_encrypted = self.encrypt(value)

    @hybrid_property
    def full_name(self) -> str:
        return self.first_name + " " + self.last_name

    @property
    def can_admin(self) -> bool:
        return self.user_role == UserRole.admin

    @property
    def can_edit(self) -> bool:
        return self.user_role in [UserRole.admin, UserRole.editor]

    @property
    def can_write(self) -> bool:
        return self.user_role in [UserRole.admin, UserRole.editor,
                                  UserRole.writer]

    @property
    def can_read(self) -> bool:
        return self.user_role in [UserRole.admin, UserRole.editor,
                                  UserRole.writer, UserRole.reader]

    @property
    def userpic_url(self):
        if self.userpic_filename:
            return cfg.USERPIC_BASE_URL + self.userpic_filename

    @property
    def userpic_path(self):
        if self.userpic_filename:
            return os.path.join(cfg.USERPIC_BASE_PATH, self.userpic_filename)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "created_date": self.created_date,
            "updated_date": self.updated_date,
            "last_login_date": self.last_login_date,
            "user_role": self.user_role.value,
            "is_active": self.is_active,
            "user_login": self.user_login,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "user_signature": self.user_signature,
            "user_contacts": self.user_contacts,
            "userpic_url": self.userpic_url,
        }
