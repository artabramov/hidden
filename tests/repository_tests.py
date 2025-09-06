import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock, AsyncMock, call
from app.repository import Repository


class RepositoryTest(unittest.IsolatedAsyncioTestCase):

    async def test_init(self):
        from app.managers.entity_manager import EntityManager
        from app.managers.cache_manager import CacheManager

        session_mock = MagicMock()
        cache_mock = MagicMock()
        dummy_class_mock = MagicMock()

        config = SimpleNamespace(REDIS_ENABLED=True, REDIS_EXPIRE=60)

        repository = Repository(
            session_mock, cache_mock, dummy_class_mock, config
        )

        self.assertTrue(isinstance(repository.entity_manager, EntityManager))
        self.assertEqual(repository.entity_manager.session, session_mock)
        self.assertTrue(isinstance(repository.cache_manager, CacheManager))
        self.assertEqual(repository.cache_manager.cache, cache_mock)
        self.assertEqual(repository.entity_class, dummy_class_mock)

    async def test_insert_commit_true(self):
        dummy_class_mock = MagicMock(__tablename__="dummies")
        dummy_mock = MagicMock()

        config = SimpleNamespace(REDIS_ENABLED=True, REDIS_EXPIRE=60)
        repository = Repository(None, None, dummy_class_mock, config)
        repository.entity_manager = AsyncMock()
        repository.cache_manager = AsyncMock()

        result = await repository.insert(dummy_mock, commit=True)
        self.assertIsNone(result)

        repository.entity_manager.insert.assert_called_once_with(
            dummy_mock, commit=True)

    async def test_insert_commit_false(self):
        dummy_class_mock = MagicMock(__tablename__="dummies")
        dummy_mock = MagicMock()

        config = SimpleNamespace(REDIS_ENABLED=True, REDIS_EXPIRE=60)
        repository = Repository(None, None, dummy_class_mock, config)
        repository.entity_manager = AsyncMock()
        repository.cache_manager = AsyncMock()

        result = await repository.insert(dummy_mock, commit=False)
        self.assertIsNone(result)

        repository.entity_manager.insert.assert_called_once_with(
            dummy_mock, commit=False)
        repository.cache_manager.set.assert_not_called()

    async def test_select_redis_enabled(self):
        dummy_class_mock = MagicMock(__tablename__="dummies", _cacheable=True)
        dummy_mock = MagicMock(id=123)

        config = SimpleNamespace(REDIS_ENABLED=True, REDIS_EXPIRE=60)
        repository = Repository(None, None, dummy_class_mock, config)
        repository.entity_manager = AsyncMock()
        repository.cache_manager = AsyncMock()
        repository.cache_manager.get.return_value = dummy_mock

        result = await repository.select(id=dummy_mock.id)
        self.assertEqual(result, dummy_mock)

        repository.entity_manager.select.assert_not_called()
        repository.entity_manager.select_by.assert_not_called()
        repository.cache_manager.get.assert_called_once_with(
            dummy_class_mock, dummy_mock.id)
        repository.cache_manager.set.assert_called_once_with(dummy_mock)

    async def test_select_redis_disabled(self):
        dummy_class_mock = MagicMock(__tablename__="dummies", _cacheable=True)
        dummy_mock = MagicMock(id=123)

        config = SimpleNamespace(REDIS_ENABLED=False, REDIS_EXPIRE=60)
        repository = Repository(None, None, dummy_class_mock, config)
        repository.entity_manager = AsyncMock()
        repository.entity_manager.select.return_value = dummy_mock
        repository.cache_manager = AsyncMock()

        result = await repository.select(id=dummy_mock.id)
        self.assertEqual(result, dummy_mock)

        repository.entity_manager.select.assert_called_once_with(
            dummy_class_mock, dummy_mock.id)
        repository.entity_manager.select_by.assert_not_called()
        repository.cache_manager.get.assert_not_called()
        repository.cache_manager.set.assert_not_called()

    async def test_select_cacheable_true(self):
        dummy_class_mock = MagicMock(__tablename__="dummies", _cacheable=True)
        dummy_mock = MagicMock(id=123)

        config = SimpleNamespace(REDIS_ENABLED=True, REDIS_EXPIRE=60)
        repository = Repository(None, None, dummy_class_mock, config)
        repository.entity_manager = AsyncMock()
        repository.entity_manager.select.return_value = dummy_mock
        repository.cache_manager = AsyncMock()
        repository.cache_manager.get.return_value = None

        result = await repository.select(id=dummy_mock.id)
        self.assertEqual(result, dummy_mock)

        repository.entity_manager.select.assert_called_once_with(
            dummy_class_mock, dummy_mock.id)
        repository.entity_manager.select_by.assert_not_called()
        repository.cache_manager.get.assert_called_once_with(
            dummy_class_mock, dummy_mock.id)
        repository.cache_manager.set.assert_called_once_with(dummy_mock)

    async def test_select_cacheable_false(self):
        dummy_class_mock = MagicMock(__tablename__="dummies", _cacheable=False)
        dummy_mock = MagicMock(id=123)

        config = SimpleNamespace(REDIS_ENABLED=True, REDIS_EXPIRE=60)
        repository = Repository(None, None, dummy_class_mock, config)
        repository.entity_manager = AsyncMock()
        repository.entity_manager.select.return_value = dummy_mock
        repository.cache_manager = AsyncMock()

        result = await repository.select(id=dummy_mock.id)
        self.assertEqual(result, dummy_mock)

        repository.entity_manager.select.assert_called_once_with(
            dummy_class_mock, dummy_mock.id)
        repository.entity_manager.select_by.assert_not_called()
        repository.cache_manager.get.assert_not_called()
        repository.cache_manager.set.assert_not_called()

    async def test_select_by_cacheable_true(self):
        dummy_class_mock = MagicMock(__tablename__="dummies", _cacheable=True)
        dummy_mock = MagicMock(key="value")

        config = SimpleNamespace(REDIS_ENABLED=True, REDIS_EXPIRE=60)
        repository = Repository(None, None, dummy_class_mock, config)
        repository.entity_manager = AsyncMock()
        repository.entity_manager.select_by.return_value = dummy_mock
        repository.cache_manager = AsyncMock()

        result = await repository.select(key__eq=dummy_mock.key)
        self.assertEqual(result, dummy_mock)

        repository.entity_manager.select.assert_not_called()
        repository.entity_manager.select_by.assert_called_once_with(
            dummy_class_mock, key__eq=dummy_mock.key
        )
        repository.cache_manager.get.assert_not_called()
        repository.cache_manager.set.assert_called_once_with(dummy_mock)

    async def test_select_by_cacheable_false(self):
        dummy_class_mock = MagicMock(__tablename__="dummies", _cacheable=False)
        dummy_mock = MagicMock(key="value")

        config = SimpleNamespace(REDIS_ENABLED=True, REDIS_EXPIRE=60)
        repository = Repository(None, None, dummy_class_mock, config)
        repository.entity_manager = AsyncMock()
        repository.entity_manager.select_by.return_value = dummy_mock
        repository.cache_manager = AsyncMock()

        result = await repository.select(key__eq=dummy_mock.key)
        self.assertEqual(result, dummy_mock)

        repository.entity_manager.select.assert_not_called()
        repository.entity_manager.select_by.assert_called_once_with(
            dummy_class_mock, key__eq=dummy_mock.key
        )
        repository.cache_manager.get.assert_not_called()
        repository.cache_manager.set.assert_not_called()

    async def test_select_by_redis_enabled(self):
        dummy_class_mock = MagicMock(__tablename__="dummies", _cacheable=True)
        dummy_mock = MagicMock(key="value")

        config = SimpleNamespace(REDIS_ENABLED=True, REDIS_EXPIRE=60)
        repository = Repository(None, None, dummy_class_mock, config)
        repository.entity_manager = AsyncMock()
        repository.entity_manager.select_by.return_value = dummy_mock
        repository.cache_manager = AsyncMock()

        result = await repository.select(key__eq=dummy_mock.key)
        self.assertEqual(result, dummy_mock)

        repository.entity_manager.select.assert_not_called()
        repository.entity_manager.select_by.assert_called_once_with(
            dummy_class_mock, key__eq=dummy_mock.key
        )
        repository.cache_manager.get.assert_not_called()
        repository.cache_manager.set.assert_called_once_with(dummy_mock)

    async def test_select_by_redis_disabled(self):
        dummy_class_mock = MagicMock(__tablename__="dummies", _cacheable=True)
        dummy_mock = MagicMock(key="value")

        config = SimpleNamespace(REDIS_ENABLED=False, REDIS_EXPIRE=60)
        repository = Repository(None, None, dummy_class_mock, config)
        repository.entity_manager = AsyncMock()
        repository.entity_manager.select_by.return_value = dummy_mock
        repository.cache_manager = AsyncMock()

        result = await repository.select(key__eq=dummy_mock.key)
        self.assertEqual(result, dummy_mock)

        repository.entity_manager.select.assert_not_called()
        repository.entity_manager.select_by.assert_called_once_with(
            dummy_class_mock, key__eq=dummy_mock.key
        )
        repository.cache_manager.get.assert_not_called()
        repository.cache_manager.set.assert_not_called()

    async def test_select_all_cacheable_true(self):
        dummy_class_mock = MagicMock(__tablename__="dummies", _cacheable=True)
        dummy_mocks = [MagicMock(key="value"), MagicMock(key="value")]

        config = SimpleNamespace(REDIS_ENABLED=True, REDIS_EXPIRE=60)
        repository = Repository(None, None, dummy_class_mock, config)
        repository.entity_manager = AsyncMock()
        repository.entity_manager.select_all.return_value = dummy_mocks
        repository.cache_manager = AsyncMock()

        result = await repository.select_all(key__eq=dummy_mocks[0].key)
        self.assertListEqual(result, dummy_mocks)

        repository.entity_manager.select_all.assert_called_once_with(
            dummy_class_mock, key__eq=dummy_mocks[0].key)
        self.assertEqual(repository.cache_manager.set.call_count, 2)
        self.assertListEqual(
            repository.cache_manager.set.call_args_list,
            [call(dummy_mocks[0]), call(dummy_mocks[1])])

    async def test_select_all_cacheable_false(self):
        dummy_class_mock = MagicMock(__tablename__="dummies", _cacheable=False)
        dummy_mocks = [MagicMock(key="value"), MagicMock(key="value")]

        config = SimpleNamespace(REDIS_ENABLED=True, REDIS_EXPIRE=60)
        repository = Repository(None, None, dummy_class_mock, config)
        repository.entity_manager = AsyncMock()
        repository.entity_manager.select_all.return_value = dummy_mocks
        repository.cache_manager = AsyncMock()

        result = await repository.select_all(key__eq=dummy_mocks[0].key)
        self.assertListEqual(result, dummy_mocks)

        repository.entity_manager.select_all.assert_called_once_with(
            dummy_class_mock, key__eq=dummy_mocks[0].key)
        repository.cache_manager.set.assert_not_called()

    async def test_select_all_redis_enabled(self):
        dummy_class_mock = MagicMock(__tablename__="dummies", _cacheable=True)
        dummy_mocks = [MagicMock(key="value"), MagicMock(key="value")]

        config = SimpleNamespace(REDIS_ENABLED=True, REDIS_EXPIRE=60)
        repository = Repository(None, None, dummy_class_mock, config)
        repository.entity_manager = AsyncMock()
        repository.entity_manager.select_all.return_value = dummy_mocks
        repository.cache_manager = AsyncMock()

        result = await repository.select_all(key__eq=dummy_mocks[0].key)
        self.assertListEqual(result, dummy_mocks)

        repository.entity_manager.select_all.assert_called_once_with(
            dummy_class_mock, key__eq=dummy_mocks[0].key)
        self.assertEqual(repository.cache_manager.set.call_count, 2)
        self.assertListEqual(
            repository.cache_manager.set.call_args_list,
            [call(dummy_mocks[0]), call(dummy_mocks[1])])

    async def test_select_all_redis_disabled(self):
        dummy_class_mock = MagicMock(__tablename__="dummies", _cacheable=True)
        dummy_mocks = [MagicMock(key="value"), MagicMock(key="value")]

        config = SimpleNamespace(REDIS_ENABLED=False, REDIS_EXPIRE=60)
        repository = Repository(None, None, dummy_class_mock, config)
        repository.entity_manager = AsyncMock()
        repository.entity_manager.select_all.return_value = dummy_mocks
        repository.cache_manager = AsyncMock()

        result = await repository.select_all(key__eq=dummy_mocks[0].key)
        self.assertListEqual(result, dummy_mocks)

        repository.entity_manager.select_all.assert_called_once_with(
            dummy_class_mock, key__eq=dummy_mocks[0].key)
        repository.cache_manager.set.assert_not_called()

    async def test_update_cacheable_commit_true(self):
        dummy_class_mock = MagicMock(__tablename__="dummies", _cacheable=True)
        dummy_mock = MagicMock()

        config = SimpleNamespace(REDIS_ENABLED=True, REDIS_EXPIRE=60)
        repository = Repository(None, None, dummy_class_mock, config)
        repository.entity_manager = AsyncMock()
        repository.cache_manager = AsyncMock()

        result = await repository.update(dummy_mock, commit=True)
        self.assertIsNone(result)

        repository.entity_manager.update.assert_called_once_with(
            dummy_mock, commit=True)
        repository.cache_manager.delete.assert_called_once_with(dummy_mock)

    async def test_update_cacheable_commit_false(self):
        dummy_class_mock = MagicMock(__tablename__="dummies", _cacheable=True)
        dummy_mock = MagicMock()

        config = SimpleNamespace(REDIS_ENABLED=True, REDIS_EXPIRE=60)
        repository = Repository(None, None, dummy_class_mock, config)
        repository.entity_manager = AsyncMock()
        repository.cache_manager = AsyncMock()

        result = await repository.update(dummy_mock, commit=False)
        self.assertIsNone(result)

        repository.entity_manager.update.assert_called_once_with(
            dummy_mock, commit=False)
        repository.cache_manager.delete.assert_called_once_with(dummy_mock)

    async def test_update_uncacheable_commit_true(self):
        dummy_class_mock = MagicMock(__tablename__="dummies", _cacheable=False)
        dummy_mock = MagicMock()

        config = SimpleNamespace(REDIS_ENABLED=True, REDIS_EXPIRE=60)
        repository = Repository(None, None, dummy_class_mock, config)
        repository.entity_manager = AsyncMock()
        repository.cache_manager = AsyncMock()

        result = await repository.update(dummy_mock, commit=True)
        self.assertIsNone(result)

        repository.entity_manager.update.assert_called_once_with(
            dummy_mock, commit=True)
        repository.cache_manager.set.assert_not_called()
        repository.cache_manager.delete.assert_not_called()

    async def test_update_uncacheable_commit_false(self):
        dummy_class_mock = MagicMock(__tablename__="dummies", _cacheable=False)
        dummy_mock = MagicMock()

        config = SimpleNamespace(REDIS_ENABLED=True, REDIS_EXPIRE=60)
        repository = Repository(None, None, dummy_class_mock, config)
        repository.entity_manager = AsyncMock()
        repository.cache_manager = AsyncMock()

        result = await repository.update(dummy_mock, commit=False)
        self.assertIsNone(result)

        repository.entity_manager.update.assert_called_once_with(
            dummy_mock, commit=False)
        repository.cache_manager.set.assert_not_called()
        repository.cache_manager.delete.assert_not_called()

    async def test_update_redis_enabled(self):
        dummy_class_mock = MagicMock(__tablename__="dummies", _cacheable=True)
        dummy_mock = MagicMock()

        config = SimpleNamespace(REDIS_ENABLED=True, REDIS_EXPIRE=60)
        repository = Repository(None, None, dummy_class_mock, config)
        repository.entity_manager = AsyncMock()
        repository.cache_manager = AsyncMock()

        result = await repository.update(dummy_mock, commit=True)
        self.assertIsNone(result)

        repository.entity_manager.update.assert_called_once_with(
            dummy_mock, commit=True)
        repository.cache_manager.set.assert_not_called()
        repository.cache_manager.delete.assert_called_once_with(dummy_mock)

    async def test_update_redis_disabled(self):
        dummy_class_mock = MagicMock(__tablename__="dummies", _cacheable=True)
        dummy_mock = MagicMock()

        config = SimpleNamespace(REDIS_ENABLED=False, REDIS_EXPIRE=60)
        repository = Repository(None, None, dummy_class_mock, config)
        repository.entity_manager = AsyncMock()
        repository.cache_manager = AsyncMock()

        result = await repository.update(dummy_mock, commit=True)
        self.assertIsNone(result)

        repository.entity_manager.update.assert_called_once_with(
            dummy_mock, commit=True)
        repository.cache_manager.set.assert_not_called()
        repository.cache_manager.delete.assert_not_called()

    async def test_delete_cacheable_commit_true(self):
        dummy_class_mock = MagicMock(__tablename__="dummies", _cacheable=True)
        dummy_mock = MagicMock()

        config = SimpleNamespace(REDIS_ENABLED=True, REDIS_EXPIRE=60)
        repository = Repository(None, None, dummy_class_mock, config)
        repository.entity_manager = AsyncMock()
        repository.cache_manager = AsyncMock()

        result = await repository.delete(dummy_mock, commit=True)
        self.assertIsNone(result)

        repository.entity_manager.delete.assert_called_once_with(
            dummy_mock, commit=True)
        repository.cache_manager.delete.assert_called_once_with(dummy_mock)

    async def test_delete_cacheable_commit_false(self):
        dummy_class_mock = MagicMock(__tablename__="dummies", _cacheable=True)
        dummy_mock = MagicMock()

        config = SimpleNamespace(REDIS_ENABLED=True, REDIS_EXPIRE=60)
        repository = Repository(None, None, dummy_class_mock, config)
        repository.entity_manager = AsyncMock()
        repository.cache_manager = AsyncMock()

        result = await repository.delete(dummy_mock, commit=False)
        self.assertIsNone(result)

        repository.entity_manager.delete.assert_called_once_with(
            dummy_mock, commit=False)
        repository.cache_manager.delete.assert_called_once_with(dummy_mock)

    async def test_delete_uncacheable_commit_true(self):
        dummy_class_mock = MagicMock(__tablename__="dummies", _cacheable=False)
        dummy_mock = MagicMock()

        config = SimpleNamespace(REDIS_ENABLED=True, REDIS_EXPIRE=60)
        repository = Repository(None, None, dummy_class_mock, config)
        repository.entity_manager = AsyncMock()
        repository.cache_manager = AsyncMock()

        result = await repository.delete(dummy_mock, commit=True)
        self.assertIsNone(result)

        repository.entity_manager.delete.assert_called_once_with(
            dummy_mock, commit=True)
        repository.cache_manager.delete.assert_not_called()

    async def test_delete_uncacheable_commit_false(self):
        dummy_class_mock = MagicMock(__tablename__="dummies", _cacheable=False)
        dummy_mock = MagicMock()

        config = SimpleNamespace(REDIS_ENABLED=True, REDIS_EXPIRE=60)
        repository = Repository(None, None, dummy_class_mock, config)
        repository.entity_manager = AsyncMock()
        repository.cache_manager = AsyncMock()

        result = await repository.delete(dummy_mock, commit=False)
        self.assertIsNone(result)

        repository.entity_manager.delete.assert_called_once_with(
            dummy_mock, commit=False)
        repository.cache_manager.delete.assert_not_called()

    async def test_delete_redis_enabled(self):
        dummy_class_mock = MagicMock(__tablename__="dummies", _cacheable=True)
        dummy_mock = MagicMock()

        config = SimpleNamespace(REDIS_ENABLED=True, REDIS_EXPIRE=60)
        repository = Repository(None, None, dummy_class_mock, config)
        repository.entity_manager = AsyncMock()
        repository.cache_manager = AsyncMock()

        result = await repository.delete(dummy_mock, commit=True)
        self.assertIsNone(result)

        repository.entity_manager.delete.assert_called_once_with(
            dummy_mock, commit=True)
        repository.cache_manager.delete.assert_called_once_with(dummy_mock)

    async def test_delete_redis_disabled(self):
        dummy_class_mock = MagicMock(__tablename__="dummies", _cacheable=True)
        dummy_mock = MagicMock()

        config = SimpleNamespace(REDIS_ENABLED=False, REDIS_EXPIRE=60)
        repository = Repository(None, None, dummy_class_mock, config)
        repository.entity_manager = AsyncMock()
        repository.cache_manager = AsyncMock()

        result = await repository.delete(dummy_mock, commit=True)
        self.assertIsNone(result)

        repository.entity_manager.delete.assert_called_once_with(
            dummy_mock, commit=True)
        repository.cache_manager.delete.assert_not_called()

    async def test_delete_from_cache_entity_cacheable(self):
        dummy_class_mock = MagicMock(__tablename__="dummies", _cacheable=True)
        dummy_mock = MagicMock()

        config = SimpleNamespace(REDIS_ENABLED=True, REDIS_EXPIRE=60)
        repository = Repository(None, None, dummy_class_mock, config)
        repository.entity_manager = AsyncMock()
        repository.cache_manager = AsyncMock()

        result = await repository.delete_from_cache(dummy_mock)
        self.assertIsNone(result)

        self.assertListEqual(repository.entity_manager.mock_calls, [])
        repository.cache_manager.delete.assert_called_once_with(dummy_mock)

    async def test_delete_from_cache_entity_uncacheable(self):
        dummy_class_mock = MagicMock(__tablename__="dummies", _cacheable=False)
        dummy_mock = MagicMock()

        config = SimpleNamespace(REDIS_ENABLED=True, REDIS_EXPIRE=60)
        repository = Repository(None, None, dummy_class_mock, config)
        repository.entity_manager = AsyncMock()
        repository.cache_manager = AsyncMock()

        result = await repository.delete_from_cache(dummy_mock)
        self.assertIsNone(result)

        self.assertListEqual(repository.entity_manager.mock_calls, [])
        repository.cache_manager.delete.assert_not_called()

    async def test_delete_from_cache_redis_enabled(self):
        dummy_class_mock = MagicMock(__tablename__="dummies", _cacheable=True)
        dummy_mock = MagicMock()

        config = SimpleNamespace(REDIS_ENABLED=True, REDIS_EXPIRE=60)
        repository = Repository(None, None, dummy_class_mock, config)
        repository.entity_manager = AsyncMock()
        repository.cache_manager = AsyncMock()

        result = await repository.delete_from_cache(dummy_mock)
        self.assertIsNone(result)

        self.assertListEqual(repository.entity_manager.mock_calls, [])
        repository.cache_manager.delete.assert_called_once_with(dummy_mock)

    async def test_delete_from_cache_redis_disabled(self):
        dummy_class_mock = MagicMock(__tablename__="dummies", _cacheable=True)
        dummy_mock = MagicMock()

        config = SimpleNamespace(REDIS_ENABLED=False, REDIS_EXPIRE=60)
        repository = Repository(None, None, dummy_class_mock, config)
        repository.entity_manager = AsyncMock()
        repository.cache_manager = AsyncMock()

        result = await repository.delete_from_cache(dummy_mock)
        self.assertIsNone(result)

        self.assertListEqual(repository.entity_manager.mock_calls, [])
        repository.cache_manager.delete.assert_not_called()

    async def test_delete_all_commit_true(self):
        dummy_class_mock = MagicMock(__tablename__="dummies", _cacheable=True)

        config = SimpleNamespace(REDIS_ENABLED=True, REDIS_EXPIRE=60)
        repository = Repository(None, None, dummy_class_mock, config)
        repository.entity_manager = AsyncMock()
        repository.cache_manager = AsyncMock()

        result = await repository.delete_all(commit=True, key__eq="value")
        self.assertIsNone(result)

        repository.entity_manager.delete_all.assert_called_once_with(
            dummy_class_mock, commit=True, key__eq="value")
        repository.cache_manager.delete_all.assert_called_once_with(
            dummy_class_mock)

    async def test_delete_all_commit_false(self):
        dummy_class_mock = MagicMock(__tablename__="dummies", _cacheable=True)

        config = SimpleNamespace(REDIS_ENABLED=True, REDIS_EXPIRE=60)
        repository = Repository(None, None, dummy_class_mock, config)
        repository.entity_manager = AsyncMock()
        repository.cache_manager = AsyncMock()

        result = await repository.delete_all(commit=False, key__eq="value")
        self.assertIsNone(result)

        repository.entity_manager.delete_all.assert_called_once_with(
            dummy_class_mock, commit=False, key__eq="value")
        repository.cache_manager.delete_all.assert_called_once_with(
            dummy_class_mock)

    async def test_delete_all_cacheable(self):
        dummy_class_mock = MagicMock(__tablename__="dummies", _cacheable=True)

        config = SimpleNamespace(REDIS_ENABLED=True, REDIS_EXPIRE=60)
        repository = Repository(None, None, dummy_class_mock, config)
        repository.entity_manager = AsyncMock()
        repository.cache_manager = AsyncMock()

        result = await repository.delete_all(commit=True, key__eq="value")
        self.assertIsNone(result)

        repository.entity_manager.delete_all.assert_called_once_with(
            dummy_class_mock, commit=True, key__eq="value")
        repository.cache_manager.delete_all.assert_called_once_with(
            dummy_class_mock)

    async def test_delete_all_uncacheable(self):
        dummy_class_mock = MagicMock(__tablename__="dummies", _cacheable=False)

        config = SimpleNamespace(REDIS_ENABLED=True, REDIS_EXPIRE=60)
        repository = Repository(None, None, dummy_class_mock, config)
        repository.entity_manager = AsyncMock()
        repository.cache_manager = AsyncMock()

        result = await repository.delete_all(commit=True, key__eq="value")
        self.assertIsNone(result)

        repository.entity_manager.delete_all.assert_called_once_with(
            dummy_class_mock, commit=True, key__eq="value")
        repository.cache_manager.delete_all.assert_not_called()

    async def test_delete_all_redis_enabled(self):
        dummy_class_mock = MagicMock(__tablename__="dummies", _cacheable=True)

        config = SimpleNamespace(REDIS_ENABLED=True, REDIS_EXPIRE=60)
        repository = Repository(None, None, dummy_class_mock, config)
        repository.entity_manager = AsyncMock()
        repository.cache_manager = AsyncMock()

        result = await repository.delete_all(commit=True, key__eq="value")
        self.assertIsNone(result)

        repository.entity_manager.delete_all.assert_called_once_with(
            dummy_class_mock, commit=True, key__eq="value")
        repository.cache_manager.delete_all.assert_called_once_with(
            dummy_class_mock)

    async def test_delete_all_redis_disabled(self):
        dummy_class_mock = MagicMock(__tablename__="dummies", _cacheable=True)

        config = SimpleNamespace(REDIS_ENABLED=False, REDIS_EXPIRE=60)
        repository = Repository(None, None, dummy_class_mock, config)
        repository.entity_manager = AsyncMock()
        repository.cache_manager = AsyncMock()

        result = await repository.delete_all(commit=True, key__eq="value")
        self.assertIsNone(result)

        repository.entity_manager.delete_all.assert_called_once_with(
            dummy_class_mock, commit=True, key__eq="value")
        repository.cache_manager.delete_all.assert_not_called()

    async def test_delete_all_from_cache_entity_cacheable(self):
        dummy_class_mock = MagicMock(__tablename__="dummies", _cacheable=True)

        config = SimpleNamespace(REDIS_ENABLED=True, REDIS_EXPIRE=60)
        repository = Repository(None, None, dummy_class_mock, config)
        repository.entity_manager = AsyncMock()
        repository.cache_manager = AsyncMock()

        result = await repository.delete_all_from_cache()
        self.assertIsNone(result)

        repository.entity_manager.delete_all.assert_not_called()
        repository.cache_manager.delete_all.assert_called_once_with(
            dummy_class_mock
        )

    async def test_delete_all_from_cache_entity_uncacheable(self):
        dummy_class_mock = MagicMock(__tablename__="dummies", _cacheable=False)

        config = SimpleNamespace(REDIS_ENABLED=True, REDIS_EXPIRE=60)
        repository = Repository(None, None, dummy_class_mock, config)
        repository.entity_manager = AsyncMock()
        repository.cache_manager = AsyncMock()

        result = await repository.delete_all_from_cache()
        self.assertIsNone(result)

        repository.entity_manager.delete_all.assert_not_called()
        repository.cache_manager.delete_all.assert_not_called()

    async def test_delete_all_from_cache_redis_enabled(self):
        dummy_class_mock = MagicMock(__tablename__="dummies", _cacheable=True)

        config = SimpleNamespace(REDIS_ENABLED=True, REDIS_EXPIRE=60)
        repository = Repository(None, None, dummy_class_mock, config)
        repository.entity_manager = AsyncMock()
        repository.cache_manager = AsyncMock()

        result = await repository.delete_all_from_cache()
        self.assertIsNone(result)

        repository.entity_manager.delete_all.assert_not_called()
        repository.cache_manager.delete_all.assert_called_once_with(
            dummy_class_mock
        )

    async def test_delete_all_from_cache_redis_disabled(self):
        dummy_class_mock = MagicMock(__tablename__="dummies", _cacheable=True)

        config = SimpleNamespace(REDIS_ENABLED=False, REDIS_EXPIRE=60)
        repository = Repository(None, None, dummy_class_mock, config)
        repository.entity_manager = AsyncMock()
        repository.cache_manager = AsyncMock()

        result = await repository.delete_all_from_cache()
        self.assertIsNone(result)

        repository.entity_manager.delete_all.assert_not_called()
        repository.cache_manager.delete_all.assert_not_called()

    async def test_count_all(self):
        dummy_class_mock = MagicMock()
        dummies_count = 123

        config = SimpleNamespace(REDIS_ENABLED=False, REDIS_EXPIRE=60)
        repository = Repository(None, None, dummy_class_mock, config)
        repository.entity_manager = AsyncMock()
        repository.entity_manager.count_all.return_value = dummies_count

        result = await repository.count_all(key__eq="value")
        self.assertEqual(result, dummies_count)

        repository.entity_manager.count_all.assert_called_once_with(
            dummy_class_mock, key__eq="value")

    async def test_sum_all(self):
        dummy_class_mock = MagicMock()
        dummies_sum = 123

        config = SimpleNamespace(REDIS_ENABLED=False, REDIS_EXPIRE=60)
        repository = Repository(None, None, dummy_class_mock, config)
        repository.entity_manager = AsyncMock()
        repository.entity_manager.sum_all.return_value = dummies_sum

        result = await repository.sum_all("key", key__eq="value")
        self.assertEqual(result, dummies_sum)

        repository.entity_manager.sum_all.assert_called_once_with(
            dummy_class_mock, "key", key__eq="value")

    async def test_commit(self):
        dummy_class_mock = MagicMock()
        config = SimpleNamespace(REDIS_ENABLED=False, REDIS_EXPIRE=60)
        repository = Repository(None, None, dummy_class_mock, config)
        repository.entity_manager = AsyncMock()

        result = await repository.commit()
        self.assertIsNone(result)

        repository.entity_manager.commit.assert_called_once()

    async def test_rollback(self):
        dummy_class_mock = MagicMock()
        config = SimpleNamespace(REDIS_ENABLED=False, REDIS_EXPIRE=60)
        repository = Repository(None, None, dummy_class_mock, config)
        repository.entity_manager = AsyncMock()

        result = await repository.rollback()
        self.assertIsNone(result)

        repository.entity_manager.rollback.assert_called_once()
