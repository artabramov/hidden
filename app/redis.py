"""
Provides an asynchronous Redis connection handler for caching
and initialization.
"""

import redis.asyncio as redis
from app.config import get_config

cfg = get_config()


async def get_cache():
    """
    Establishes and yields an asynchronous Redis connection, ensuring
    it is properly closed after use.
    """
    try:
        conn = redis.Redis(
            host=cfg.REDIS_HOST, port=cfg.REDIS_PORT,
            decode_responses=cfg.REDIS_DECODE_RESPONSES)
        yield conn
    finally:
        if conn:
            await conn.close()


async def init_cache():
    """
    Initializes the Redis cache by establishing a connection
    and flushing the database.
    """
    cache_gen = get_cache()
    async for cache in cache_gen:
        await cache.flushdb()
