
import os
import time
import asyncio
from sqlalchemy import Column, Integer, BigInteger, String, ForeignKey, event
from sqlalchemy.orm import relationship
from app.postgres import Base
from app.managers.file_manager import FileManager
from app.helpers.encrypt_helper import (
    encrypt_str, decrypt_str, encrypt_int, decrypt_int)
from app.config import get_config
from app.log import get_log

cfg = get_config()
log = get_log()


class Shard(Base):
    __tablename__ = "documents_shards"
    _cacheable = False

    id = Column(BigInteger, primary_key=True)

    created_date_encrypted = Column(
        String(64), nullable=False,
        default=lambda: encrypt_int(int(time.time())))

    document_id = Column(
        BigInteger, ForeignKey("documents.id"),
        nullable=False, index=True)

    # value length up to 255
    shard_filename_encrypted = Column(
        String(384), nullable=False)

    shard_index = Column(
        Integer, index=True, nullable=False)

    shard_document = relationship(
        "Document", back_populates="document_shards", lazy="noload")

    def __init__(self, document_id: int, shard_filename: str,
                 shard_index: int):
        self.document_id = document_id
        self.shard_filename = shard_filename
        self.shard_index = shard_index

    @property
    def created_date(self):
        return decrypt_int(self.created_date_encrypted)

    @property
    def shard_filename(self):
        return decrypt_str(self.shard_filename_encrypted)

    @shard_filename.setter
    def shard_filename(self, shard_filename: str):
        self.shard_filename_encrypted = encrypt_str(shard_filename)

    @property
    def shard_path(self):
        return os.path.join(cfg.DOCUMENTS_PATH, self.shard_filename)


@event.listens_for(Shard, "after_delete")
def after_delete_listener(mapper, connection, shard: Shard):
    asyncio.get_event_loop().create_task(delete_file(shard.shard_path))


async def delete_file(shard_path: str):
    try:
        await FileManager.delete(shard_path)
    except Exception as e:
        log.error("File deletion failed; module=shard_model; "
                  "function=delete_file; e=%s;" % str(e))
