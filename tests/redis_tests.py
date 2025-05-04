
import unittest
import types
from unittest.mock import patch, AsyncMock
from app.redis import get_cache


class CacheTest(unittest.IsolatedAsyncioTestCase):

    @patch('app.redis.redis.Redis')
    async def test_cache_open(self, RedisMock):
        redis_mock = AsyncMock()
        RedisMock.return_value = redis_mock

        result = get_cache()

        self.assertIsInstance(result, types.AsyncGeneratorType,
                              "Expected async generator")

        async for conn in result:
            self.assertEqual(conn, redis_mock,
                             f"Expected Redis connection, got {conn}")

    @patch('app.redis.redis.Redis')
    async def test_cache_close(self, RedisMock):
        redis_mock = AsyncMock()
        RedisMock.return_value = redis_mock

        result = get_cache()

        self.assertIsInstance(result, types.AsyncGeneratorType,
                              "Expected async generator")

        async for conn in result:
            self.assertEqual(conn, redis_mock,
                             f"Expected Redis connection, got {conn}")

        redis_mock.close.assert_awaited_once()
        redis_mock.close.assert_awaited_once_with()


if __name__ == "__main__":
    unittest.main()
