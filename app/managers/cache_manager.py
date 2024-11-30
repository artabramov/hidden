"""
The module provides the CacheManager class for managing caching
operations with Redis for SQLAlchemy entities. The CacheManager class
offers methods to set, get, delete, and delete all cached SQLAlchemy
model instances. It leverages Redis for efficient storage and retrieval
and supports asynchronous operations to enhance performance.
"""

from typing import Type, Optional, Union
from sqlalchemy.ext.serializer import dumps, loads
from sqlalchemy.orm import DeclarativeBase
from redis import Redis
from app.decorators.timed_decorator import timed
from app.config import get_config
from app.log import get_log

cfg = get_config()
log = get_log()


class CacheManager:
    """
    Manages caching operations for SQLAlchemy models using Redis. This
    class provides methods for setting, retrieving, deleting, and
    bulk-deleting cached SQLAlchemy model instances. It uses Redis for
    storage and supports asynchronous operations to handle caching
    efficiently.
    """

    def __init__(self, cache: Redis):
        """
        Initializes the CacheManager with a Redis cache instance. This
        sets up the CacheManager to use the provided Redis instance for
        all caching operations.
        """
        self.cache = cache

    def _get_key(self, entity: Type[DeclarativeBase],
                 entity_id: Union[int, str]) -> str:
        """
        Constructs a cache key based on the SQLAlchemy model's table
        name and the model's ID. The key is formatted as table_name:id
        for storing or retrieving the SQLAlchemy model in the Redis
        cache.
        """
        return "%s:%s" % (entity.__tablename__, entity_id)

    @timed
    async def set(self, entity: DeclarativeBase):
        """
        Caches an SQLAlchemy model instance by serializing it and
        storing it in Redis with an expiration time.
        """
        key = self._get_key(entity, entity.id)
        await self.cache.set(key, dumps(entity), ex=cfg.REDIS_EXPIRE)

    @timed
    async def get(self, cls: Type[DeclarativeBase],
                  entity_id: int) -> Optional[DeclarativeBase]:
        """
        Retrieves an SQLAlchemy model instance from the cache by
        fetching the serialized model from Redis and deserializing it.
        """
        key = self._get_key(cls, entity_id)
        entity_bytes = await self.cache.get(key)
        return loads(entity_bytes) if entity_bytes else None

    @timed
    async def delete(self, entity: DeclarativeBase):
        """
        Removes an SQLAlchemy model instance from the cache by deleting
        the cache entry associated with the given model.
        """
        key = self._get_key(entity, entity.id)
        await self.cache.delete(key)

    @timed
    async def delete_all(self, cls: Type[DeclarativeBase]):
        """
        Removes all cached instances of a given SQLAlchemy model class
        by deleting all cache entries related to the specified class.
        """
        key_pattern = self._get_key(cls, "*")
        for key in await self.cache.keys(key_pattern):
            await self.cache.delete(key)

    @timed
    async def erase(self):
        """
        Clears all cache entries in Redis, effectively erasing all
        cached SQLAlchemy model instances.
        """
        await self.cache.flushdb()
