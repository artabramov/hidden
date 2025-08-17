"""
The module provides the class for managing caching operations with Redis
for SQLAlchemy entities. The class offers methods to set, get and delete
cached SQLAlchemy objects.
"""

from typing import Type, Optional, Union
from sqlalchemy.ext.serializer import dumps, loads
from sqlalchemy.orm import DeclarativeBase
from redis.asyncio import Redis
from app.config import get_config
from app.decorators.timed_decorator import timed

cfg = get_config()


class CacheManager:
    """
    Manages caching operations for SQLAlchemy models using Redis. This
    class provides methods for setting, retrieving and deleting cached
    SQLAlchemy model instances. It uses Redis for storage and supports
    asynchronous operations to handle caching efficiently.
    """

    def __init__(self, cache: Redis):
        """Initializes the class with a Redis connection."""
        self.cache = cache

    def _get_cache_key(self, entity: Type[DeclarativeBase],
                       entity_id: Union[int, str]) -> str:
        """
        Constructs a cache key based on the table name and the model ID.
        The key is formatted as table_name:id for storing or retrieving
        the SQLAlchemy model in the Redis cache.
        """
        return "%s:%s" % (entity.__tablename__, entity_id)

    @timed
    async def set(self, entity: DeclarativeBase):
        """
        Caches an SQLAlchemy model instance by serializing it and
        storing it in Redis cache with an expiration time.
        """
        key = self._get_cache_key(entity, entity.id)
        await self.cache.set(key, dumps(entity), ex=cfg.REDIS_EXPIRE)

    @timed
    async def get(self, cls: Type[DeclarativeBase],
                  entity_id: int) -> Optional[DeclarativeBase]:
        """
        Retrieves an SQLAlchemy model instance from the Redis cache by
        fetching the serialized model from Redis and deserializing it.
        """
        key = self._get_cache_key(cls, entity_id)
        entity_bytes = await self.cache.get(key)
        return loads(entity_bytes) if entity_bytes else None

    @timed
    async def delete(self, entity: DeclarativeBase):
        """
        Removes an SQLAlchemy model instance from the Redis cache by
        deleting the cache entry associated with the given model.
        """
        key = self._get_cache_key(entity, entity.id)
        await self.cache.delete(key)

    @timed
    async def delete_all(self, cls: Type[DeclarativeBase]):
        """
        Removes all cached instances of a given SQLAlchemy model class
        by deleting all cache entries related to the specified class.
        """
        key_pattern = self._get_cache_key(cls, "*")
        for key in await self.cache.keys(key_pattern):
            await self.cache.delete(key)

    @timed
    async def erase(self):
        """Clears all cached entries from Redis cache."""
        await self.cache.flushdb()
