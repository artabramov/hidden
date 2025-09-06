import unittest
from types import SimpleNamespace
from unittest.mock import patch
from app.redis import RedisClient, get_cache, init_cache


class FakeRedis:
    def __init__(self):
        self.closed = False
        self.pings = 0

    async def ping(self):
        self.pings += 1
        return True

    async def close(self):
        self.closed = True


class CacheNoSideEffectsTest(unittest.IsolatedAsyncioTestCase):
    @patch("app.redis.redis.Redis")
    async def test_client_constructs_and_close(self, redis_ctor_mock):
        fake = FakeRedis()
        redis_ctor_mock.return_value = fake
        client = RedisClient(
            host="localhost", port=6379, decode_responses=True)
        redis_ctor_mock.assert_called_once_with(
            host="localhost", port=6379, decode_responses=True)
        self.assertIs(client.redis, fake)

        await client.close()
        self.assertTrue(fake.closed)

    @patch("app.redis.redis.Redis")
    async def test_get_cache_yields_shared_client(self, redis_ctor_mock):
        fake = FakeRedis()
        redis_ctor_mock.return_value = fake
        client = RedisClient(
            host="localhost", port=6379, decode_responses=True)

        request = SimpleNamespace(app=SimpleNamespace(
            state=SimpleNamespace(redis_client=client)))

        agen = get_cache(request)
        yielded = await agen.__anext__()
        self.assertIs(yielded, fake)

        try:
            await agen.asend(None)
        except StopAsyncIteration:
            pass

        self.assertFalse(fake.closed)

    @patch("app.redis.redis.Redis")
    async def test_init_cache_calls_ping(self, redis_ctor_mock):
        fake = FakeRedis()
        redis_ctor_mock.return_value = fake
        client = RedisClient(
            host="localhost", port=6379, decode_responses=True)

        await init_cache(client)
        self.assertEqual(fake.pings, 1)
