"""
The module defines an SQLAlchemy model for document revisions. It
describes the structure of the revision entity, including its fields
such as filename, size, and MIME type. The module also manages the
relationships between revisions and other entities like users and
documents. It includes functionality for handling encrypted thumbnail
filenames and provides methods for deleting associated files when a
revision is deleted.
"""

import os
import time
from sqlalchemy import Column, Integer, BigInteger, String, ForeignKey, event
from sqlalchemy.orm import relationship
from app.database import Base
from app.config import get_config
from app.managers.file_manager import FileManager
import asyncio
from app.log import get_log
from app.helpers.encryption_helper import encrypt_value, decrypt_value

cfg = get_config()
log = get_log()


class Revision(Base):
    """
    SQLAlchemy model representing a document revision. It contains
    metadata for each revision, such as the filename, size, MIME type,
    and associated user and document. The class also manages encrypted
    thumbnail filenames and provides properties for retrieving the
    thumbnail's path and URL. The revision entity is linked to its
    corresponding document and user, and it includes relationships with
    other entities such as downloads and shards. Additionally, it
    ensures that associated files are deleted asynchronously when a
    revision is removed from the database.
    """
    __tablename__ = "documents_revisions"
    _cacheable = True

    id = Column(BigInteger, primary_key=True)
    created_date = Column(Integer, index=True,
                          default=lambda: int(time.time()))
    user_id = Column(BigInteger, ForeignKey("users.id"), index=True)
    document_id = Column(BigInteger, ForeignKey("documents.id"), index=True)
    revision_filename = Column(String(256), index=True, nullable=False)
    revision_size = Column(BigInteger, index=True, nullable=False)
    revision_mimetype = Column(String(256), index=True, nullable=False)
    thumbnail_filename_encrypted = Column(
        String(256), nullable=True, unique=True)

    revision_user = relationship(
        "User", back_populates="user_revisions", lazy="joined")

    revision_document = relationship(
        "Document", back_populates="document_revisions", lazy="joined",
        foreign_keys=[document_id])

    revision_downloads = relationship(
        "Download", back_populates="download_revision", lazy="noload",
        cascade="all, delete-orphan")

    revision_shards = relationship(
        "Shard", back_populates="shard_revision", lazy="joined",
        cascade="all, delete-orphan")

    def __init__(self, user_id: int, document_id: int, revision_filename: str,
                 revision_size: int, revision_mimetype: str,
                 thumbnail_filename: str = None):
        self.user_id = user_id
        self.document_id = document_id
        self.revision_filename = revision_filename
        self.revision_size = revision_size
        self.revision_mimetype = revision_mimetype
        self.thumbnail_filename = thumbnail_filename

    @property
    def thumbnail_filename(self) -> str:
        """
        Retrieves the decrypted thumbnail filename for the revision.
        Returns None if the thumbnail filename is not encrypted.
        """
        return (decrypt_value(self.thumbnail_filename_encrypted)
                if self.thumbnail_filename_encrypted else None)

    @thumbnail_filename.setter
    def thumbnail_filename(self, value: str):
        """
        Sets the encrypted thumbnail filename for the revision.
        """
        self.thumbnail_filename_encrypted = (
            encrypt_value(value) if value else None)

    @property
    def thumbnail_path(self):
        """
        Constructs and returns the file system path for the revision's
        thumbnail.
        """
        return os.path.join(cfg.THUMBNAILS_BASE_PATH, self.thumbnail_filename)

    @property
    def thumbnail_url(self):
        """
        Constructs and returns the URL for the revision's thumbnail.
        """
        if self.thumbnail_filename:
            return cfg.THUMBNAILS_BASE_URL + self.thumbnail_filename

    async def to_dict(self):
        """
        Converts the revision instance into a dictionary representation,
        including relevant details like the revision filename, size,
        MIME type, and thumbnail URL.
        """
        return {
            "id": self.id,
            "created_date": self.created_date,
            "user_id": self.user_id,
            "user_name": self.revision_user.full_name,
            "document_id": self.document_id,
            "revision_filename": self.revision_filename,
            "revision_size": self.revision_size,
            "revision_mimetype": self.revision_mimetype,
            "thumbnail_url": self.thumbnail_url,
        }


@event.listens_for(Revision, "after_delete")
def after_delete_listener(mapper, connection, revision: Revision):
    """
    Event listener triggered after a revision entity is deleted.
    Schedules tasks to delete the revision's main file and the
    associated thumbnail file, if one exists.
    """
    asyncio.get_event_loop().create_task(delete_revision(revision))

    if revision.thumbnail_filename:
        asyncio.get_event_loop().create_task(delete_thumbnail(revision))


async def delete_revision(revision: Revision):
    """
    Asynchronously deletes the main file associated with the specified
    revision entity. Logs any errors that occur during the deletion
    process.
    """
    try:
        await FileManager.delete(revision.revision_path)

    except Exception as e:
        log.error("File deletion failed; module=revision_model; "
                  "function=delete_revision; e=%s;" % str(e))


async def delete_thumbnail(revision: Revision):
    """
    Asynchronously deletes the thumbnail file associated with the
    specified revision entity. Logs any errors that occur during the
    deletion process.
    """
    if revision.thumbnail_filename:
        try:
            await FileManager.delete(revision.thumbnail_path)
        except Exception as e:
            log.error("File deletion failed; module=revision_model; "
                      "function=delete_thumbnail; e=%s;" % str(e))
