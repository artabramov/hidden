"""
The module provides asynchronous access to the Redis cache. This module
defines a function to establish a connection to Redis using configuration
settings and ensures the connection is properly closed after use.
"""

import redis.asyncio as redis
from app.config import get_config

cfg = get_config()


async def get_cache():
    """
    Establishes and yields an asynchronous Redis connection using the
    configured host, port, and decoding settings. Ensures the connection
    is closed after use.
    """
    try:
        conn = redis.Redis(host=cfg.REDIS_HOST, port=cfg.REDIS_PORT,
                           decode_responses=cfg.REDIS_DECODE)
        yield conn
    finally:
        await conn.close()
