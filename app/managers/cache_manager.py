"""
Redis-backed cache manager for SQLAlchemy ORM entities. Provides
TTL-based caching of ORM instances, lookup by model and primary key,
bulk invalidation per model, and full-database flush, using SQLAlchemy's
binary serialization format.
"""

from typing import Type, Optional, Union
from sqlalchemy.ext.serializer import dumps, loads
from sqlalchemy.orm import DeclarativeBase
from redis.asyncio import Redis


class CacheManager:
    """
    Manages caching operations for SQLAlchemy models using Redis. This
    class provides methods for setting, retrieving and deleting cached
    SQLAlchemy model instances. It uses Redis for storage and supports
    asynchronous operations to handle caching efficiently.
    """

    def __init__(self, cache: Redis, expire: int):
        """Initializes the class with a Redis connection."""
        self.cache = cache
        self.expire = expire

    def _get_cache_key(self, cls: Type[DeclarativeBase],
                       entity_id: Union[int, str]) -> str:
        """
        Constructs a cache key based on the table name and the model ID.
        The key is formatted as table_name:id for storing or retrieving
        the SQLAlchemy model in the Redis cache.
        """
        return f"{cls.__tablename__}:{entity_id}"

    async def set(self, entity: DeclarativeBase) -> None:
        """
        Caches an SQLAlchemy model instance by serializing it and
        storing it in Redis cache with an expiration time.
        """
        key = self._get_cache_key(type(entity), entity.id)
        await self.cache.set(key, dumps(entity), ex=self.expire)

    async def get(self, cls: Type[DeclarativeBase],
                  entity_id: Union[int, str]) -> Optional[DeclarativeBase]:
        """
        Retrieves an SQLAlchemy model instance from the Redis cache by
        fetching the serialized model from Redis and deserializing it.
        """
        key = self._get_cache_key(cls, entity_id)
        payload = await self.cache.get(key)
        return loads(payload) if payload is not None else None

    async def delete(self, entity: DeclarativeBase) -> None:
        """
        Removes an SQLAlchemy model instance from the Redis cache by
        deleting the cache entry associated with the given model.
        """
        key = self._get_cache_key(type(entity), entity.id)
        await self.cache.delete(key)

    async def delete_all(self, cls: Type[DeclarativeBase]) -> None:
        """
        Removes all cached instances of a given SQLAlchemy model class
        by deleting all cache entries related to the specified class.
        """
        key_pattern = self._get_cache_key(cls, "*")
        async for key in self.cache.scan_iter(match=key_pattern):
            await self.cache.delete(key)

    async def erase(self) -> None:
        """Clears all cached entries from Redis cache."""
        await self.cache.flushdb()
