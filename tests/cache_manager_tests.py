import unittest
from unittest.mock import MagicMock, AsyncMock, patch, call
from app.managers.cache_manager import CacheManager


class CacheManagerTest(unittest.IsolatedAsyncioTestCase):

    async def test_init(self):
        cache_mock = AsyncMock()
        cache_manager = CacheManager(cache_mock)

        self.assertEqual(cache_manager.cache, cache_mock)

    @patch("app.managers.cache_manager.loads")
    async def test_get_integer(self, loads_mock):
        cache_mock = AsyncMock()
        cache_manager = CacheManager(cache_mock)

        cls_mock = MagicMock(__tablename__="objs")

        result = await cache_manager.get(cls_mock, 123)
        self.assertEqual(result, loads_mock.return_value)

        cache_mock.get.assert_called_once_with("objs:123")
        loads_mock.assert_called_once_with(cache_mock.get.return_value)

    @patch("app.managers.cache_manager.loads")
    async def test_get_asterisk(self, loads_mock):
        cache_mock = AsyncMock()
        cache_manager = CacheManager(cache_mock)

        cls_mock = MagicMock(__tablename__="objs")

        result = await cache_manager.get(cls_mock, "*")
        self.assertEqual(result, loads_mock.return_value)

        cache_mock.get.assert_called_once_with("objs:*")
        loads_mock.assert_called_once_with(cache_mock.get.return_value)

    @patch("app.managers.cache_manager.loads")
    async def test_get_not_found(self, loads_mock):
        cache_mock = AsyncMock()
        cache_manager = CacheManager(cache_mock)

        cache_mock.get.return_value = None
        cls_mock = MagicMock(__tablename__="objs")

        result = await cache_manager.get(cls_mock, 123)
        self.assertIsNone(result)

        cache_mock.get.assert_called_once_with("objs:123")
        loads_mock.assert_not_called()

    @patch("app.managers.cache_manager.cfg")
    @patch("app.managers.cache_manager.dumps")
    async def test_set(self, dumps_mock, cfg_mock):
        cache_mock = AsyncMock()
        cache_manager = CacheManager(cache_mock)

        obj_mock = MagicMock(__tablename__="objs", id=123)

        result = await cache_manager.set(obj_mock)
        self.assertIsNone(result)

        dumps_mock.assert_called_once_with(obj_mock)
        cache_mock.set.assert_called_once_with(
            "objs:123", dumps_mock.return_value, ex=cfg_mock.REDIS_EXPIRE)

    async def test_delete(self):
        cache_mock = AsyncMock()
        cache_manager = CacheManager(cache_mock)

        obj_mock = MagicMock(__tablename__="objs", id=123)

        result = await cache_manager.delete(obj_mock)
        self.assertIsNone(result)

        cache_mock.delete.assert_called_once_with("objs:123")

    async def test_delete_all(self):
        cache_mock = AsyncMock()
        cache_manager = CacheManager(cache_mock)

        cls_mock = MagicMock(__tablename__="objs")
        key_1, key_2, key_3 = "objs:1", "objs:2", "objs:3"
        cache_mock.keys.return_value = [key_1, key_2, key_3]

        result = await cache_manager.delete_all(cls_mock)
        self.assertIsNone(result)

        cache_mock.keys.assert_called_once_with("objs:*")
        self.assertEqual(cache_mock.delete.call_count, 3)
        self.assertListEqual(cache_mock.delete.call_args_list,
                             [call(key_1), call(key_2), call(key_3)])

    async def test_erase(self):
        cache_mock = AsyncMock()
        cache_manager = CacheManager(cache_mock)

        result = await cache_manager.erase()
        self.assertIsNone(result)

        cache_mock.flushdb.assert_called_once()


if __name__ == "__main__":
    unittest.main()
