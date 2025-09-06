"""
Provides an asynchronous Redis client managed via FastAPI lifespan:
the client is created from runtime settings, stored in app.state for
reuse, exposed through a request-scoped dependency, and optionally
initialized on startup.
"""

from typing import AsyncGenerator
from starlette.requests import Request
import redis.asyncio as redis
from redis.asyncio import Redis as RedisType


class RedisClient:
    """
    Holds a shared asyncio Redis client built from configuration and
    intended to be instantiated during application startup and reused
    across requests via app.state.
    """
    def __init__(self, *, host: str, port: int, decode_responses: bool = True):
        self.redis: RedisType = redis.Redis(
            host=host,
            port=port,
            decode_responses=decode_responses
        )

    async def close(self) -> None:
        """Close the underlying connection pool on application shutdown."""
        await self.redis.close()


async def get_cache(request: Request) -> AsyncGenerator[RedisType, None]:
    """
    Yield the shared Redis client from app.state without closing it per
    request so the connection pool can be reused efficiently across the
    application.
    """
    client: RedisClient = request.app.state.redis_client
    yield client.redis


async def init_cache(client: RedisClient) -> None:
    """
    Optionally initialize the cache by checking connectivity and
    performing startup tasks like a database flush if desired.
    """
    await client.redis.ping()
