"""
The module provides an asynchronous Redis connection handler.
"""

import redis.asyncio as redis
from app.config import get_config

cfg = get_config()


async def get_cache():
    """
    Establishes and yields an asynchronous Redis connection which is
    closed after use.
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
    cache_gen = get_cache()
    async for cache in cache_gen:
        await cache.flushdb()
