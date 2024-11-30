"""
This module contains unit tests for the CacheManager class, which
handles caching operations with Redis. It includes tests for
initialization, key generation, and methods for setting, retrieving,
and deleting cache entries, as well as managing cases where cache
entries are missing. The tests use the asynctest and unittest libraries
to ensure that CacheManager functions correctly under various scenarios.
"""

import asynctest
import unittest
from unittest.mock import MagicMock, AsyncMock, patch, call


class CacheManagerTestCase(asynctest.TestCase):

    async def setUp(self):
        """Sets up the test environment."""
        from app.managers.cache_manager import CacheManager

        self.cache_mock = AsyncMock()
        self.cache_manager = CacheManager(self.cache_mock)

    async def tearDown(self):
        """Cleans up after tests."""
        del self.cache_mock
        del self.cache_manager

    async def test__init(self):
        """Tests that the CacheManager is correctly initialized."""
        self.assertEqual(self.cache_manager.cache, self.cache_mock)

    async def test__get_key_int(self):
        """Tests the _get_key method for integer IDs."""
        dummy_mock = MagicMock(__tablename__="dummies")

        result = self.cache_manager._get_key(dummy_mock, 123)
        self.assertEqual(result, "dummies:123")

    async def test__get_key_asterisk(self):
        """Tests the _get_key method for wildcard (*) IDs."""
        dummy_mock = MagicMock(__tablename__="dummies")

        result = self.cache_manager._get_key(dummy_mock, "*")
        self.assertEqual(result, "dummies:*")

    @patch("app.managers.cache_manager.cfg")
    @patch("app.managers.cache_manager.dumps")
    async def test__set(self, dumps_mock, cfg_mock):
        """Tests the set method of CacheManager to cache an object."""
        dummy_mock = MagicMock(__tablename__="dummies", id=123)

        result = await self.cache_manager.set(dummy_mock)
        self.assertIsNone(result)

        dumps_mock.assert_called_once_with(dummy_mock)
        self.cache_mock.set.assert_called_once_with(
            "dummies:123", dumps_mock.return_value, ex=cfg_mock.REDIS_EXPIRE)

    @patch("app.managers.cache_manager.loads")
    async def test__get(self, loads_mock):
        """Tests the get method to retrieve a cached object."""
        dummy_class_mock = MagicMock(__tablename__="dummies")

        result = await self.cache_manager.get(dummy_class_mock, 123)
        self.assertEqual(result, loads_mock.return_value)

        self.cache_mock.get.assert_called_once_with("dummies:123")
        loads_mock.assert_called_once_with(self.cache_mock.get.return_value)

    @patch("app.managers.cache_manager.loads")
    async def test__get_none(self, loads_mock):
        """Tests the get method when the cache returns None."""
        self.cache_mock.get.return_value = None
        dummy_class_mock = MagicMock(__tablename__="dummies")

        result = await self.cache_manager.get(dummy_class_mock, 123)
        self.assertIsNone(result)

        self.cache_mock.get.assert_called_once_with("dummies:123")
        loads_mock.assert_not_called()

    async def test__delete(self):
        """Tests the delete method to remove an item from cache."""
        dummy_mock = MagicMock(__tablename__="dummies", id=123)

        result = await self.cache_manager.delete(dummy_mock)
        self.assertIsNone(result)

        self.cache_mock.delete.assert_called_once_with("dummies:123")

    async def test__delete_all(self):
        """Tests the delete_all method to remove all items."""
        dummy_class_mock = MagicMock(__tablename__="dummies")
        key_1, key_2, key_3 = "dummies:1", "dummies:2", "dummies:3"
        self.cache_mock.keys.return_value = [key_1, key_2, key_3]

        result = await self.cache_manager.delete_all(dummy_class_mock)
        self.assertIsNone(result)

        self.cache_mock.keys.assert_called_once_with("dummies:*")
        self.assertEqual(self.cache_mock.delete.call_count, 3)
        self.assertListEqual(self.cache_mock.delete.call_args_list,
                             [call(key_1), call(key_2), call(key_3)])

    async def test__erase(self):
        """Tests the cache erase."""
        result = await self.cache_manager.erase()
        self.assertIsNone(result)

        self.cache_mock.flushdb.assert_called_once()


if __name__ == "__main__":
    unittest.main()
