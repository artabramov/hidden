import unittest
from unittest.mock import MagicMock, AsyncMock, patch, call
from app.managers.cache_manager import CacheManager


class CacheManagerTest(unittest.IsolatedAsyncioTestCase):

    async def test_init(self):
        cache_mock = AsyncMock()
        cm = CacheManager(cache_mock, expire=60)

        self.assertEqual(cm.cache, cache_mock)
        self.assertEqual(cm.expire, 60)

    @patch("app.managers.cache_manager.loads")
    async def test_get_integer(self, loads_mock):
        cache_mock = AsyncMock()
        cm = CacheManager(cache_mock, expire=60)

        cls_mock = MagicMock(__tablename__="objs")

        result = await cm.get(cls_mock, 123)
        self.assertEqual(result, loads_mock.return_value)

        cache_mock.get.assert_called_once_with("objs:123")
        loads_mock.assert_called_once_with(cache_mock.get.return_value)

    @patch("app.managers.cache_manager.loads")
    async def test_get_asterisk(self, loads_mock):
        cache_mock = AsyncMock()
        cm = CacheManager(cache_mock, expire=60)

        cls_mock = MagicMock(__tablename__="objs")

        result = await cm.get(cls_mock, "*")
        self.assertEqual(result, loads_mock.return_value)

        cache_mock.get.assert_called_once_with("objs:*")
        loads_mock.assert_called_once_with(cache_mock.get.return_value)

    @patch("app.managers.cache_manager.loads")
    async def test_get_not_found(self, loads_mock):
        cache_mock = AsyncMock()
        cm = CacheManager(cache_mock, expire=60)

        cache_mock.get.return_value = None
        cls_mock = MagicMock(__tablename__="objs")

        result = await cm.get(cls_mock, 123)
        self.assertIsNone(result)

        cache_mock.get.assert_called_once_with("objs:123")
        loads_mock.assert_not_called()

    @patch("app.managers.cache_manager.loads")
    async def test_get_handles_string_id(self, loads_mock):
        cache = AsyncMock()
        cm = CacheManager(cache, expire=60)
        cls_mock = MagicMock(__tablename__="objs")

        await cm.get(cls_mock, "abc-123")
        cache.get.assert_called_once_with("objs:abc-123")
        loads_mock.assert_called_once_with(cache.get.return_value)

    @patch("app.managers.cache_manager.loads")
    async def test_get_calls_loads_on_empty_bytes_payload(self, loads_mock):
        cache = AsyncMock()
        cm = CacheManager(cache, expire=60)
        cls_mock = MagicMock(__tablename__="objs")
        cache.get.return_value = b""

        result = await cm.get(cls_mock, 1)
        self.assertEqual(result, loads_mock.return_value)
        loads_mock.assert_called_once_with(b"")

    async def test_get_propagates_redis_error(self):
        cache = AsyncMock()
        cm = CacheManager(cache, expire=60)
        cls_mock = MagicMock(__tablename__="objs")
        cache.get.side_effect = RuntimeError("redis down")

        with self.assertRaises(RuntimeError):
            await cm.get(cls_mock, 1)

    @patch("app.managers.cache_manager.dumps")
    async def test_set(self, dumps_mock):
        cache_mock = AsyncMock()
        cm = CacheManager(cache_mock, expire=42)

        class Obj:
            __tablename__ = "objs"
        obj = Obj()
        obj.id = 123

        result = await cm.set(obj)
        self.assertIsNone(result)

        dumps_mock.assert_called_once_with(obj)
        cache_mock.set.assert_called_once_with(
            "objs:123", dumps_mock.return_value, ex=42
        )

    @patch("app.managers.cache_manager.dumps", return_value=b"payload")
    async def test_set_respects_zero_ttl(self, _dumps_mock):
        cache = AsyncMock()
        cm = CacheManager(cache, expire=0)

        class Obj:
            __tablename__ = "objs"
        obj = Obj()
        obj.id = 7

        await cm.set(obj)

        args, kwargs = cache.set.call_args
        self.assertEqual(args[0], "objs:7")
        self.assertEqual(args[1], b"payload")

        self.assertIn("ex", kwargs)
        self.assertEqual(kwargs["ex"], 0)

    async def test_delete(self):
        cache_mock = AsyncMock()
        cm = CacheManager(cache_mock, expire=60)

        class Obj:
            __tablename__ = "objs"
        obj = Obj()
        obj.id = 123

        result = await cm.delete(obj)
        self.assertIsNone(result)

        cache_mock.delete.assert_called_once_with("objs:123")

    async def test_delete_all(self):
        cache_mock = AsyncMock()
        cm = CacheManager(cache_mock, expire=60)

        cls_mock = MagicMock(__tablename__="objs")
        key_1, key_2, key_3 = "objs:1", "objs:2", "objs:3"

        async def agen():
            for k in (key_1, key_2, key_3):
                yield k
        cache_mock.scan_iter = MagicMock(return_value=agen())

        result = await cm.delete_all(cls_mock)
        self.assertIsNone(result)

        cache_mock.scan_iter.assert_called_once_with(match="objs:*")
        self.assertEqual(cache_mock.delete.call_count, 3)
        self.assertListEqual(
            cache_mock.delete.call_args_list,
            [call(key_1), call(key_2), call(key_3)],
        )

    async def test_delete_all_handles_no_keys(self):
        cache = AsyncMock()
        cm = CacheManager(cache, expire=60)
        cls_mock = MagicMock(__tablename__="objs")

        async def agen_empty():
            if False:
                yield None
        cache.scan_iter = MagicMock(return_value=agen_empty())

        result = await cm.delete_all(cls_mock)
        self.assertIsNone(result)
        cache.scan_iter.assert_called_once_with(match="objs:*")
        cache.delete.assert_not_called()

    async def test_erase(self):
        cache_mock = AsyncMock()
        cm = CacheManager(cache_mock, expire=60)

        result = await cm.erase()
        self.assertIsNone(result)

        cache_mock.flushdb.assert_called_once()

    async def test_erase_propagates_exception(self):
        cache = AsyncMock()
        cm = CacheManager(cache, expire=60)
        cache.flushdb.side_effect = RuntimeError("no permission")

        with self.assertRaises(RuntimeError):
            await cm.erase()
