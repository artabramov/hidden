"""
The module defines a SQLAlchemy model a user entity, which defines
the structure of the user and its relationships to other entities.
"""

import os
import time
import pyotp
from typing import Union
from sqlalchemy import Column, BigInteger, String
from sqlalchemy.orm import relationship
from app.postgres import Base
from app.helpers.encrypt_helper import (
    encrypt_str, decrypt_str, encrypt_int, decrypt_int,
    encrypt_bool, decrypt_bool, hash_str)
from app.helpers.sort_helper import get_index
from app.helpers.mfa_helper import generate_mfa_secret
from app.helpers.jwt_helper import generate_jti
from app.config import get_config
from app.models.user_meta_model import UserMeta
from app.mixins.meta_mixin import MetaMixin

cfg = get_config()


class UserRole:
    """
    The possible roles a user can have. These roles determine the level
    of access and permissions a user has in the app.
    """
    reader = "reader"
    writer = "writer"
    editor = "editor"
    admin = "admin"


class User(Base, MetaMixin):
    """
    The SQLAlchemy model representing a user entity. It stores personal
    information, authentication details, and multi-factor authentication
    (MFA) data. It also manages roles, permissions, and relationships
    with other models.
    """
    __tablename__ = "users"
    _cacheable = True
    _meta = UserMeta

    id = Column(BigInteger, primary_key=True)

    # original length up to 15
    created_date_encrypted = Column(
        String(64), nullable=False,
        default=lambda: encrypt_int(int(time.time())))

    # original length up to 15
    updated_date_encrypted = Column(
        String(64), nullable=False, default=lambda: encrypt_int(0),
        onupdate=lambda: encrypt_int(int(time.time())))

    # original length up to 15
    suspended_date_encrypted = Column(
        String(64), nullable=False, default=lambda: encrypt_int(0))

    # original length up to 47
    username_encrypted = Column(String(108), nullable=False)
    username_hash = Column(String(128), nullable=False, index=True)
    username_index = Column(BigInteger, nullable=False, index=True)

    password_hash = Column(String(128), nullable=False)

    # original length up to 15
    password_attempts_encrypted = Column(String(64), nullable=False)

    # original length up to 15
    password_accepted_encrypted = Column(String(64), nullable=False)

    # original length up to 47
    first_name_encrypted = Column(String(108), nullable=False)
    first_name_index = Column(BigInteger, nullable=False, index=True)

    # original length up to 47
    last_name_encrypted = Column(String(108), nullable=False)
    last_name_index = Column(BigInteger, nullable=False, index=True)

    # original length up to 15
    user_role_encrypted = Column(String(64), nullable=False)

    # original length up to 15
    is_active_encrypted = Column(String(64), nullable=False)

    # original length up to 63
    mfa_secret_encrypted = Column(String(128), nullable=False)

    # original length up to 15
    mfa_attempts_encrypted = Column(String(64), nullable=False)

    # original length up to 47
    jti_encrypted = Column(String(108), nullable=False)

    # original length up to 4095
    user_summary_encrypted = Column(String(5504), nullable=True)

    # original length up to 79
    userpic_filename_encrypted = Column(String(152), nullable=True)

    user_meta = relationship(
        "UserMeta", back_populates="meta_user", lazy="joined",
        cascade="all, delete-orphan")

    user_collections = relationship(
        "Collection", back_populates="collection_user", lazy="noload")

    user_documents = relationship(
        "Document", back_populates="document_user", lazy="noload")

    user_settings = relationship(
        "Setting", back_populates="setting_user", lazy="noload")

    def __init__(self, username: str, password: str, first_name: str,
                 last_name: str, user_role: UserRole = UserRole.reader,
                 is_active: bool = False, user_summary: str = None):
        """
        Initializes a new user instance. It takes in the user's username,
        password, first name, last name, user role, activity status, and
        an optional user summary. The constructor also generates MFA
        secrets and assigns default values to certain fields.
        """
        self.username = username
        self.password_hash = hash_str(password)
        self.password_attempts = 0
        self.password_accepted = False
        self.first_name = first_name
        self.last_name = last_name
        self.user_role = user_role
        self.is_active = is_active
        self.mfa_secret = generate_mfa_secret()
        self.mfa_attempts = 0
        self.jti = generate_jti()
        self.user_summary = user_summary
        self.userpic_filename = None
        self.user_meta = []

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
    def suspended_date(self) -> int:
        return decrypt_int(self.suspended_date_encrypted)

    @suspended_date.setter
    def suspended_date(self, suspended_date: int):
        self.suspended_date_encrypted = encrypt_int(suspended_date)

    @property
    def username(self) -> str:
        return decrypt_str(self.username_encrypted)

    @username.setter
    def username(self, username: str):
        self.username_encrypted = encrypt_str(username)
        self.username_hash = hash_str(username)
        self.username_index = get_index(username)

    @property
    def password_attempts(self) -> int:
        return decrypt_int(self.password_attempts_encrypted)

    @password_attempts.setter
    def password_attempts(self, password_attempts: int):
        self.password_attempts_encrypted = encrypt_int(password_attempts)

    @property
    def password_accepted(self) -> bool:
        return decrypt_bool(self.password_accepted_encrypted)

    @password_accepted.setter
    def password_accepted(self, password_accepted: bool):
        self.password_accepted_encrypted = encrypt_bool(password_accepted)

    @property
    def first_name(self) -> str:
        return decrypt_str(self.first_name_encrypted)

    @first_name.setter
    def first_name(self, first_name: str):
        self.first_name_encrypted = encrypt_str(first_name)
        self.first_name_index = get_index(first_name)

    @property
    def last_name(self) -> str:
        return decrypt_str(self.last_name_encrypted)

    @last_name.setter
    def last_name(self, last_name: str):
        self.last_name_encrypted = encrypt_str(last_name)
        self.last_name_index = get_index(last_name)

    @property
    def user_role(self) -> str:
        return decrypt_str(self.user_role_encrypted)

    @user_role.setter
    def user_role(self, user_role: str):
        self.user_role_encrypted = encrypt_str(user_role)

    @property
    def is_active(self) -> bool:
        return decrypt_bool(self.is_active_encrypted)

    @is_active.setter
    def is_active(self, is_active: bool):
        self.is_active_encrypted = encrypt_bool(is_active)

    @property
    def mfa_secret(self) -> str:
        return decrypt_str(self.mfa_secret_encrypted)

    @mfa_secret.setter
    def mfa_secret(self, mfa_secret: str):
        self.mfa_secret_encrypted = encrypt_str(mfa_secret)

    @property
    def mfa_attempts(self) -> int:
        return decrypt_int(self.mfa_attempts_encrypted)

    @mfa_attempts.setter
    def mfa_attempts(self, mfa_attempts: int):
        self.mfa_attempts_encrypted = encrypt_int(mfa_attempts)

    @property
    def user_totp(self):
        totp = pyotp.TOTP(self.mfa_secret)
        return totp.now()

    @property
    def jti(self) -> str:
        return decrypt_str(self.jti_encrypted)

    @jti.setter
    def jti(self, jti: str):
        self.jti_encrypted = encrypt_str(jti)

    @property
    def user_summary(self) -> Union[str, None]:
        return decrypt_str(self.user_summary_encrypted)

    @user_summary.setter
    def user_summary(self, user_summary: str):
        self.user_summary_encrypted = encrypt_str(user_summary)

    @property
    def userpic_filename(self) -> Union[str, None]:
        return decrypt_str(self.userpic_filename_encrypted)

    @userpic_filename.setter
    def userpic_filename(self, userpic_filename: str):
        self.userpic_filename_encrypted = encrypt_str(userpic_filename)

    @property
    def userpic_path(self):
        if self.has_userpic:
            return os.path.join(cfg.USERPICS_PATH, self.userpic_filename)

    @property
    def has_userpic(self):
        return self.userpic_filename is not None

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

    async def to_dict(self) -> dict:
        return {
            "id": self.id,
            "created_date": self.created_date,
            "username": self.username,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "user_role": self.user_role,
            "is_active": self.is_active,
            "user_summary": self.user_summary,
            "userpic_filename": self.userpic_filename,
            "user_meta": {
                meta.meta_key: meta.meta_value
                for meta in self.user_meta},
        }
