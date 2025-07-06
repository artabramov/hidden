"""
The module defines a SQLAlchemy model for a setting entity. This model
represents configuration settings, including the setting's key and value,
along with the date when it was created and updated. It supports
encryption for sensitive data fields.
"""

import time
from sqlalchemy import Column, BigInteger, String, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.config import get_config
from app.postgres import Base
from app.helpers.encrypt_helper import (
    encrypt_int, decrypt_int, encrypt_str, decrypt_str, hash_str)

cfg = get_config()


class Setting(Base):
    """
    An SQLAlchemy model represents a setting entity within the app. The
    model is used to store configuration values, including metadata such
    as creation and update dates. It supports encryption for sensitive
    fields like the setting key and value and provides methods for
    handling these fields securely.
    """
    __tablename__ = "settings"
    _cacheable = False

    id = Column(BigInteger, primary_key=True)

    # original length up to 15
    created_date_encrypted = Column(
        String(64), nullable=False,
        default=lambda: encrypt_int(int(time.time())))

    # original length up to 15
    updated_date_encrypted = Column(
        String(64), nullable=False, default=lambda: encrypt_int(0),
        onupdate=lambda: encrypt_int(int(time.time())))

    user_id = Column(
        BigInteger, ForeignKey("users.id"), index=True, nullable=False)

    # value length up to 47
    setting_key_encrypted = Column(String(108), nullable=False)
    setting_key_hash = Column(String(128), nullable=False, index=True)

    setting_value_encrypted = Column(Text, nullable=True)

    setting_user = relationship(
        "User", back_populates="user_settings", lazy="joined")

    def __init__(self, user_id: int, setting_key: str, setting_value: str):
        """
        Initializes a new setting instance. This constructor accepts
        parameters for user ID, setting key, and setting value, which
        are used to set the corresponding fields for the setting entity.
        """
        self.user_id = user_id
        self.setting_key = setting_key
        self.setting_value = setting_value

    @property
    def created_date(self):
        return decrypt_int(self.created_date_encrypted)

    @property
    def updated_date(self) -> int:
        return decrypt_int(self.updated_date_encrypted)

    @updated_date.setter
    def updated_date(self, updated_date: int):
        self.updated_date_encrypted = encrypt_int(updated_date)

    @property
    def setting_key(self):
        return decrypt_str(self.setting_key_encrypted)

    @setting_key.setter
    def setting_key(self, setting_key: str):
        self.setting_key_encrypted = encrypt_str(setting_key)
        self.setting_key_hash = hash_str(setting_key)

    @property
    def setting_value(self):
        return decrypt_str(self.setting_value_encrypted)

    @setting_value.setter
    def setting_value(self, setting_value: str):
        self.setting_value_encrypted = encrypt_str(setting_value)
