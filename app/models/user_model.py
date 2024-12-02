"""
The module defines the User model for managing users in the system. The
User class includes fields for personal information, authentication
details, and multi-factor authentication (MFA). It also provides methods
to manage user roles, permissions, and security-related features. The
class establishes relationships with other models like documents,
collections, and downloads.
"""

import os
import time
import pyotp
from sqlalchemy import (Boolean, Column, BigInteger, Integer, SmallInteger,
                        String)
from sqlalchemy.ext.hybrid import hybrid_property
from app.helpers.hash_helper import get_hash
from sqlalchemy.orm import relationship
from app.config import get_config
from app.database import Base
from app.helpers.jwt_helper import jti_create
from app.helpers.encryption_helper import encrypt_value, decrypt_value

cfg = get_config()


class UserRole:
    """
    An enumeration representing the possible roles a user can have.
    These roles determine the level of access and permissions a user
    has in the system.
    """
    reader = "reader"
    writer = "writer"
    editor = "editor"
    admin = "admin"


# user_role_enum = ENUM(UserRole, name="userrole", create_type=False)


class User(Base):
    """
    The User class represents a user in the system. It stores personal
    information, authentication details, and multi-factor authentication
    (MFA) data. The class also manages roles, permissions, and
    relationships with other system models.
    """
    __tablename__ = "users"
    _cacheable = True

    id = Column(BigInteger, primary_key=True)
    created_date = Column(Integer, index=True,
                          default=lambda: int(time.time()))
    updated_date = Column(Integer, index=True, default=0,
                          onupdate=lambda: int(time.time()))
    last_login_date = Column(Integer, nullable=False, index=True, default=0)
    suspended_date = Column(Integer, nullable=False, default=0)
    user_role = Column(String(40), nullable=False, index=True)
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
    user_caption = Column(String(40), index=False, nullable=True)
    user_contacts = Column(String(512), index=False, nullable=True)
    userpic_filename_encrypted = Column(
        String(256), nullable=True, unique=True)

    user_collections = relationship(
        "Collection", back_populates="collection_user", lazy="noload")
    user_partners = relationship(
        "Partner", back_populates="partner_user", lazy="noload")
    user_documents = relationship(
        "Document", back_populates="document_user", lazy="noload")
    user_revisions = relationship(
        "Revision", back_populates="revision_user", lazy="noload")
    user_comments = relationship(
        "Comment", back_populates="comment_user", lazy="noload")
    user_downloads = relationship(
        "Download", back_populates="download_user", lazy="noload")
    user_options = relationship(
        "Option", back_populates="option_user", lazy="noload")
    user_shards = relationship(
        "Shard", back_populates="shard_user", lazy="noload")

    def __init__(self, user_role: UserRole, user_login: str,
                 user_password: str, first_name: str, last_name: str,
                 is_active: bool = False, user_caption: str = "",
                 user_contacts: str = ""):
        """
        Initializes a new user with the provided attributes. The
        password is hashed during initialization, and MFA settings are
        configured with a new secret.
        """
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
        self.mfa_secret = pyotp.random_base32()
        self.mfa_attempts = 0
        self.jti = jti_create()
        self.user_caption = user_caption
        self.user_contacts = user_contacts
        self.userpic_filename = None

    @property
    def userpic_filename(self) -> str:
        """
        Retrieves the decrypted user profile picture filename. Returns
        the decrypted filename of the user's profile picture, or None
        if not set.
        """
        return (decrypt_value(self.userpic_filename_encrypted)
                if self.userpic_filename_encrypted else None)

    @userpic_filename.setter
    def userpic_filename(self, value: str):
        """
        Sets and encrypts the user's profile picture filename.
        """
        self.userpic_filename_encrypted = (
            encrypt_value(value) if value else None)

    @property
    def mfa_secret(self) -> str:
        """
        Retrieves the decrypted multi-factor authentication (MFA) secret.
        Returns the decrypted MFA secret.
        """
        return decrypt_value(self.mfa_secret_encrypted)

    @mfa_secret.setter
    def mfa_secret(self, value: str):
        """
        Sets and encrypts the multi-factor authentication (MFA) secret.
        """
        self.mfa_secret_encrypted = encrypt_value(value)

    @property
    def mfa_url(self):
        """
        Generates the URL for setting up MFA for the user. Returns the
        URL that can be used for MFA setup for the user.
        """
        return cfg.APP_BASE_URL + cfg.APP_PREFIX + "/user/%s/mfa/%s" % (
            self.id, self.mfa_secret)

    @property
    def user_totp(self):
        """
        Generates a one-time password (OTP) for multi-factor
        authentication. Returns the current OTP generated for MFA using
        the user's secret.
        """
        totp = pyotp.TOTP(self.mfa_secret)
        return totp.now()

    @property
    def jti(self) -> str:
        """
        Retrieves the decrypted JWT identifier (JTI). Returns the
        decrypted JWT identifier.
        """
        return decrypt_value(self.jti_encrypted)

    @jti.setter
    def jti(self, value: str):
        """
        Sets and encrypts the JWT identifier (JTI).
        """
        self.jti_encrypted = encrypt_value(value)

    @hybrid_property
    def full_name(self) -> str:
        """
        Returns the full name of the user (first name and last name).
        """
        return self.first_name + " " + self.last_name

    @property
    def can_admin(self) -> bool:
        """
        Checks if the user has administrative permissions. Returns True
        if the user role is 'admin', False otherwise.
        """
        return self.user_role == UserRole.admin

    @property
    def can_edit(self) -> bool:
        """
        Checks if the user has editing permissions. Returns True if the
        user role is 'admin' or 'editor', False otherwise.
        """
        return self.user_role in [UserRole.admin, UserRole.editor]

    @property
    def can_write(self) -> bool:
        """
        Checks if the user has write permissions. Returns True if the
        user role is 'admin', 'editor', or 'writer', False otherwise.
        """
        return self.user_role in [UserRole.admin, UserRole.editor,
                                  UserRole.writer]

    @property
    def can_read(self) -> bool:
        """
        Checks if the user has read permissions. Returns True if the
        user role is 'admin', 'editor', 'writer', or 'reader', False
        otherwise.
        """
        return self.user_role in [UserRole.admin, UserRole.editor,
                                  UserRole.writer, UserRole.reader]

    @property
    def userpic_url(self):
        """
        Retrieves the URL of the user's profile picture. Returns the URL
        of the user's profile picture if available.
        """
        if self.userpic_filename:
            return cfg.USERPIC_BASE_URL + self.userpic_filename

    @property
    def userpic_path(self):
        """
        Retrieves the file path of the user's profile picture. Returns
        the file path of the user's profile picture if available.
        """
        if self.userpic_filename:
            return os.path.join(cfg.USERPIC_BASE_PATH, self.userpic_filename)

    async def to_dict(self) -> dict:
        """
        Converts the user object to a dictionary representation. Returns
        a dictionary with user details like id, login, role, etc.
        """
        return {
            "id": self.id,
            "created_date": self.created_date,
            "updated_date": self.updated_date,
            "last_login_date": self.last_login_date,
            "user_role": self.user_role,
            "is_active": self.is_active,
            "user_login": self.user_login,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "user_caption": self.user_caption,
            "user_contacts": self.user_contacts,
            "userpic_url": self.userpic_url,
        }
