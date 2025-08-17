from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis
from app.models.shard_model import Shard
from app.managers.file_manager import FileManager
from app.repository import Repository

TMP_EXTENSION = ".tmp"
SHUFFLE_LIMIT = 1


async def shuffle_shards(session: AsyncSession, cache: Redis):
    """
    Handles the process of shuffling files by copying, deleting, and
    renaming shard files. It retrieves shard information from the
    database and optionally enables a lock to prevent concurrent
    operations during the shuffle process.
    """
    shard_repository = Repository(session, cache, Shard)
    shards = await shard_repository.select_all(
        offset=0, limit=SHUFFLE_LIMIT, order_by="id", order="rand")

    for shard in shards:
        tmp_path = shard.shard_path + TMP_EXTENSION
        await FileManager.copy(shard.shard_path, tmp_path)
        await FileManager.rename(tmp_path, shard.shard_path)
