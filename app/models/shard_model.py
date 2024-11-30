"""
The module defines the Shard model for managing document shards in the
database. It includes the structure of the shard entity and its
relationships with the user and revision models. The Shard model handles
shard filenames, including encryption and decryption, and provides
methods for managing file deletion upon record deletion.
"""

import os
import time
import asyncio
from sqlalchemy import Column, Integer, BigInteger, String, ForeignKey, event
from sqlalchemy.orm import relationship
from app.database import Base
from app.managers.file_manager import FileManager
from app.helpers.encryption_helper import encrypt_value, decrypt_value
from app.config import get_config
from app.log import get_log

cfg = get_config()
log = get_log()


class Shard(Base):
    """
    Represents a shard of a document revision. Each shard is associated
    with a user and revision, and contains a filename (encrypted) and an
    index. The model provides methods for file handling, including
    encryption of shard filenames and deletion of the associated file
    when the record is deleted.
    """
    __tablename__ = "shards"
    _cacheable = False

    id = Column(BigInteger, primary_key=True)
    created_date = Column(
        Integer, index=True, default=lambda: int(time.time()))
    user_id = Column(BigInteger, ForeignKey("users.id"), index=True)
    revision_id = Column(
        BigInteger, ForeignKey("documents_revisions.id"), index=True)
    shard_filename_encrypted = Column(String(256), index=True, nullable=False)
    shard_index = Column(Integer, index=True, nullable=False)

    shard_user = relationship(
        "User", back_populates="user_shards", lazy="joined")

    shard_revision = relationship(
        "Revision", back_populates="revision_shards", lazy="joined")

    def __init__(self, user_id: int, revision_id: int, shard_filename: str,
                 shard_index: int,):
        """
        Initializes a new Shard instance. It sets the user ID, revision
        ID, shard filename, and shard index, while handling the
        encryption of the shard filename.
        """
        self.user_id = user_id
        self.revision_id = revision_id
        self.shard_filename = shard_filename
        self.shard_index = shard_index

    @property
    def shard_filename(self) -> str:
        """
        Decrypts the shard filename before returning it. This property
        allows access to the actual filename of the shard, after
        decryption.
        """
        return decrypt_value(self.shard_filename_encrypted)

    @shard_filename.setter
    def shard_filename(self, value: str):
        """
        Encrypts and stores the shard filename when setting the value.
        The setter encrypts the filename and stores it in the encrypted
        field.
        """
        self.shard_filename_encrypted = encrypt_value(value)

    @property
    def shard_path(self):
        """
        Generates the full file path for the shard based on the shard
        filename and the configured shard base path.
        """
        return os.path.join(cfg.SHARD_BASE_PATH, self.shard_filename)


@event.listens_for(Shard, "after_delete")
def after_delete_listener(mapper, connection, shard: Shard):
    """
    Triggered after the deletion of a Shard instance, this function
    schedules the deletion of the shard file from the filesystem. It
    ensures that the shard file is removed asynchronously after the
    database record is deleted.
    """
    shard_path = os.path.join(cfg.SHARD_BASE_PATH, shard.shard_filename)
    asyncio.get_event_loop().create_task(delete_file(shard_path))


async def delete_file(shard_path: str):
    """
    Asynchronously deletes the specified shard file from the filesystem.
    Any errors that occur during deletion are logged for debugging
    purposes.
    """
    try:
        await FileManager.delete(shard_path)

    except Exception as e:
        log.error("File deletion failed; module=revision_model; "
                  "function=delete_revision; e=%s;" % str(e))
