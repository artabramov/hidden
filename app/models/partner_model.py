"""
The module defines an SQLAlchemy model for partners, representing
a partner. It includes fields such as the partner's name, type, region,
website, contacts, and summary. The model handles the encryption and
decryption of the partner's profile picture filename and provides
properties for constructing the picture's URL and path. Additionally,
the module ensures that the profile picture is deleted when the partner
entity is removed from the database.
"""

import time
import os
from sqlalchemy.orm import relationship
from sqlalchemy import Column, BigInteger, Integer, ForeignKey, String, event
from app.config import get_config
from app.database import Base
import asyncio
from app.log import get_log
from app.managers.file_manager import FileManager
from app.helpers.encryption_helper import encrypt_value, decrypt_value

cfg = get_config()
log = get_log()


class Partner(Base):
    """
    SQLAlchemy model for a partner entity, which includes information
    about the partner such as their name, type, region, website, and
    contact details. It establishes relationships with the associated
    user and documents and includes methods for handling encrypted
    profile picture filenames, constructing URLs for the partner's
    picture, and ensuring file deletion when the partner is deleted.
    """
    __tablename__ = "partners"
    _cacheable = True

    id = Column(BigInteger, primary_key=True)
    created_date = Column(Integer, index=True,
                          default=lambda: int(time.time()))
    updated_date = Column(Integer, index=True,
                          onupdate=lambda: int(time.time()), default=0)
    user_id = Column(BigInteger, ForeignKey("users.id"), index=True)

    partner_name = Column(String(256), index=True, unique=True, nullable=False)
    partner_type = Column(String(256), index=True, nullable=True)
    partner_region = Column(String(256), index=True, nullable=True)
    partner_website = Column(String(256), index=True, nullable=True)
    partner_contacts = Column(String(512), index=True, nullable=True)
    partner_summary = Column(String(512), nullable=True)
    partnerpic_filename_encrypted = Column(
        String(256), nullable=True, unique=True)

    partner_user = relationship(
        "User", back_populates="user_partners", lazy="joined")

    partner_documents = relationship(
        "Document", back_populates="document_partner")

    def __init__(self, user_id: int, partner_name: str,
                 partner_type: str = None, partner_region: str = None,
                 partner_website: str = None, partner_contacts: str = None,
                 partner_summary: str = None, partnerpic_filename: str = None):
        """
        Initializes a new partner instance with the provided details
        including the partner's user association, name, type, region,
        website, contacts, and summary. Optionally initializes the
        profile picture filename.
        """
        self.user_id = user_id
        self.partner_name = partner_name
        self.partner_type = partner_type
        self.partner_region = partner_region
        self.partner_website = partner_website
        self.partner_contacts = partner_contacts
        self.partner_summary = partner_summary
        self.partnerpic_filename = partnerpic_filename

    @property
    def partnerpic_filename(self) -> str:
        """
        Retrieves the decrypted profile picture filename for the partner.
        If the filename is not encrypted, returns None.
        """
        return (decrypt_value(self.partnerpic_filename_encrypted)
                if self.partnerpic_filename_encrypted else None)

    @partnerpic_filename.setter
    def partnerpic_filename(self, value: str):
        """
        Sets the encrypted profile picture filename for the partner.
        """
        self.partnerpic_filename_encrypted = (
            encrypt_value(value) if value else None)

    @property
    def partnerpic_url(self):
        """
        Constructs and returns the URL for the partner's profile picture.
        """
        if self.partnerpic_filename:
            return cfg.PARTNERPIC_BASE_URL + self.partnerpic_filename

    @property
    def partnerpic_path(self):
        """
        Constructs and returns the file system path for the partner's
        profile picture.
        """
        if self.partnerpic_filename:
            return os.path.join(cfg.PARTNERPIC_BASE_PATH,
                                self.partnerpic_filename)

    async def to_dict(self):
        """
        Converts the partner instance into a dictionary representation,
        including relevant details like the partner's name, type, region,
        website, and profile picture URL.
        """
        return {
            "id": self.id,
            "created_date": self.created_date,
            "updated_date": self.updated_date,
            "user_id": self.user_id,
            "user_name": self.partner_user.full_name,
            "partner_name": self.partner_name,
            "partner_type": self.partner_type,
            "partner_region": self.partner_region,
            "partner_website": self.partner_website,
            "partner_contacts": self.partner_contacts,
            "partner_summary": self.partner_summary,
            "partnerpic_url": self.partnerpic_url,
        }


@event.listens_for(Partner, "after_delete")
def after_delete_listener(mapper, connection, partner: Partner):
    """
    Event listener that triggers after a partner entity is deleted.
    It attempts to delete the partner's profile picture file if it
    exists.
    """
    if partner.partnerpic_filename:
        asyncio.get_event_loop().create_task(delete_partnerpic(partner))


async def delete_partnerpic(partner: Partner):
    """
    Deletes the profile picture file associated with a partner if it
    exists. Handles exceptions and logs any errors that occur during
    deletion.
    """
    try:
        await FileManager.delete(partner.partnerpic_path)

    except Exception as e:
        log.error("File deletion failed; module=partner_model; "
                  "function=delete_partnerpic; e=%s;" % str(e))
