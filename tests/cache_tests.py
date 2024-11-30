import unittest
from unittest.mock import patch, AsyncMock
from app.cache import get_cache
import types


class TestCache(unittest.IsolatedAsyncioTestCase):

    @patch('app.cache.redis.Redis')
    async def test_get_cache_connection(self, mock_redis):
        """Test that the Redis connection is correctly established."""
        mock_redis_instance = AsyncMock()
        mock_redis.return_value = mock_redis_instance

        result = get_cache()

        self.assertIsInstance(result, types.AsyncGeneratorType,
                              "Expected async generator")

        async for conn in result:
            self.assertEqual(conn, mock_redis_instance,
                             f"Expected Redis connection, got {conn}")

    @patch('app.cache.redis.Redis')
    async def test_get_cache_closes_connection(self, mock_redis):
        """Test that the Redis connection is correctly closed after use."""
        mock_redis_instance = AsyncMock()
        mock_redis.return_value = mock_redis_instance

        result = get_cache()

        self.assertIsInstance(result, types.AsyncGeneratorType,
                              "Expected async generator")

        async for conn in result:
            self.assertEqual(conn, mock_redis_instance,
                             f"Expected Redis connection, got {conn}")

        mock_redis_instance.close.assert_awaited_once()
        mock_redis_instance.close.assert_awaited_once_with()


if __name__ == '__main__':
    unittest.main()
