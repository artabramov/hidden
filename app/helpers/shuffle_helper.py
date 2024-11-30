"""
The module provides functionality for shuffling files. It handles the
process of copying, deleting, and renaming files based on shard
information retrieved from the database. The function also supports
locking mechanisms to prevent concurrent operations during the shuffle
process.
"""

from sqlalchemy.ext.asyncio import AsyncSession
from redis import Redis
from app.models.shard_model import Shard
from app.managers.file_manager import FileManager
from app.helpers.lock_helper import lock_enable, lock_disable
from app.repository import Repository
from app.config import get_config

cfg = get_config()


async def shuffle(session: AsyncSession, cache: Redis):
    """
    Handles the process of shuffling files by copying, deleting, and
    renaming shard files. It retrieves shard information from the
    database and optionally enables a lock to prevent concurrent
    operations during the shuffle process.
    """
    shard_repository = Repository(session, cache, Shard)
    shards = await shard_repository.select_all(
        offset=0, limit=cfg.SHUFFLE_LIMIT, order_by="id", order="rand")

    if shards and cfg.SHUFFLE_LOCKED:
        await lock_enable()

    for shard in shards:
        copy_path = shard.shard_path + cfg.SHUFFLE_EXTENSION
        await FileManager.copy(shard.shard_path, copy_path)
        await FileManager.delete(shard.shard_path)
        await FileManager.rename(copy_path, shard.shard_path)

    if shards and cfg.SHUFFLE_LOCKED:
        await lock_disable()
