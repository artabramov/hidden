"""
Unit tests for the Repository class, validating its methods for
initializing, inserting, selecting, updating, deleting, and counting
entities, both cacheable and uncacheable. The tests ensure that
interactions with the entity manager and cache manager occur correctly
and that repository operations perform as expected under various
conditions, using mocking to simulate dependencies and validate
behavior.
"""

import asynctest
import unittest
from unittest.mock import MagicMock, AsyncMock, call
from app.repository import Repository


class RepositoryTestCase(asynctest.TestCase):
    """Test case for Repository class."""

    def setUp(self):
        """Set up the test case environment."""
        pass

    def tearDown(self):
        """Clean up the test case environment."""
        pass

    async def test__init(self):
        """Test Repository initialization."""
        from app.managers.entity_manager import EntityManager
        from app.managers.cache_manager import CacheManager

        session_mock = MagicMock()
        cache_mock = MagicMock()
        dummy_class_mock = MagicMock()

        repository = Repository(session_mock, cache_mock, dummy_class_mock)

        self.assertTrue(isinstance(repository.entity_manager, EntityManager))
        self.assertEqual(repository.entity_manager.session, session_mock)
        self.assertTrue(isinstance(repository.cache_manager, CacheManager))
        self.assertEqual(repository.cache_manager.cache, cache_mock)
        self.assertEqual(repository.entity_class, dummy_class_mock)

    async def test__insert_cacheable_commit_true(self):
        """Test insert with cacheable entity and commit True."""
        dummy_class_mock = MagicMock(__tablename__="dummies", _cacheable=True)
        dummy_mock = MagicMock()

        repository = Repository(None, None, dummy_class_mock)
        repository.entity_manager = AsyncMock()
        repository.cache_manager = AsyncMock()

        result = await repository.insert(dummy_mock, commit=True)
        self.assertIsNone(result)

        repository.entity_manager.insert.assert_called_once_with(
            dummy_mock, commit=True)

    async def test__insert_cacheable_commit_false(self):
        """Test insert with cacheable entity and commit False."""
        dummy_class_mock = MagicMock(__tablename__="dummies", _cacheable=True)
        dummy_mock = MagicMock()

        repository = Repository(None, None, dummy_class_mock)
        repository.entity_manager = AsyncMock()
        repository.cache_manager = AsyncMock()

        result = await repository.insert(dummy_mock, commit=False)
        self.assertIsNone(result)

        repository.entity_manager.insert.assert_called_once_with(
            dummy_mock, commit=False)
        repository.cache_manager.set.assert_not_called()

    async def test__insert_uncacheable_commit_true(self):
        """Test insert with uncacheable entity and commit True."""
        dummy_class_mock = MagicMock(__tablename__="dummies", _cacheable=False)
        dummy_mock = MagicMock()

        repository = Repository(None, None, dummy_class_mock)
        repository.entity_manager = AsyncMock()
        repository.cache_manager = AsyncMock()

        result = await repository.insert(dummy_mock, commit=True)
        self.assertIsNone(result)

        repository.entity_manager.insert.assert_called_once_with(
            dummy_mock, commit=True)
        repository.cache_manager.set.assert_not_called()

    async def test__insert_uncacheable_commit_false(self):
        """Test insert with uncacheable entity and commit False."""
        dummy_class_mock = MagicMock(__tablename__="dummies", _cacheable=False)
        dummy_mock = MagicMock()

        repository = Repository(None, None, dummy_class_mock)
        repository.entity_manager = AsyncMock()
        repository.cache_manager = AsyncMock()

        result = await repository.insert(dummy_mock, commit=False)
        self.assertIsNone(result)

        repository.entity_manager.insert.assert_called_once_with(
            dummy_mock, commit=False)
        repository.cache_manager.set.assert_not_called()

    async def test__select_id_cacheable_cached(self):
        """Test select by id with cacheable entity when cached."""
        dummy_class_mock = MagicMock(__tablename__="dummies", _cacheable=True)
        dummy_mock = MagicMock(id=123)

        repository = Repository(None, None, dummy_class_mock)
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

    async def test__select_id_cacheable_uncached(self):
        """Test select by id with cacheable entity when not cached."""
        dummy_class_mock = MagicMock(__tablename__="dummies", _cacheable=True)
        dummy_mock = MagicMock(id=123)

        repository = Repository(None, None, dummy_class_mock)
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

    async def test__select_id_uncacheable(self):
        """Test select by id with uncacheable entity."""
        dummy_class_mock = MagicMock(__tablename__="dummies", _cacheable=False)
        dummy_mock = MagicMock(id=123)

        repository = Repository(None, None, dummy_class_mock)
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

    async def test__select_by_cacheable(self):
        """Test select by criteria with cacheable entity."""
        dummy_class_mock = MagicMock(__tablename__="dummies", _cacheable=True)
        dummy_mock = MagicMock(key="value")

        repository = Repository(None, None, dummy_class_mock)
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

    async def test__select_by_uncacheable(self):
        """Test select by criteria with uncacheable entity."""
        dummy_class_mock = MagicMock(__tablename__="dummies", _cacheable=False)
        dummy_mock = MagicMock(key="value")

        repository = Repository(None, None, dummy_class_mock)
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

    async def test__select_all_cacheable(self):
        """Test select all with cacheable entities."""
        dummy_class_mock = MagicMock(__tablename__="dummies", _cacheable=True)
        dummy_mocks = [MagicMock(key="value"), MagicMock(key="value")]

        repository = Repository(None, None, dummy_class_mock)
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

    async def test__select_all_uncacheable(self):
        """Test select all with uncacheable entities."""
        dummy_class_mock = MagicMock(__tablename__="dummies", _cacheable=False)
        dummy_mocks = [MagicMock(key="value"), MagicMock(key="value")]

        repository = Repository(None, None, dummy_class_mock)
        repository.entity_manager = AsyncMock()
        repository.entity_manager.select_all.return_value = dummy_mocks
        repository.cache_manager = AsyncMock()

        result = await repository.select_all(key__eq=dummy_mocks[0].key)
        self.assertListEqual(result, dummy_mocks)

        repository.entity_manager.select_all.assert_called_once_with(
            dummy_class_mock, key__eq=dummy_mocks[0].key)
        repository.cache_manager.set.assert_not_called()

    async def test__update_cacheable_commit_true(self):
        """Test update with cacheable entity and commit True."""
        dummy_class_mock = MagicMock(__tablename__="dummies", _cacheable=True)
        dummy_mock = MagicMock()

        repository = Repository(None, None, dummy_class_mock)
        repository.entity_manager = AsyncMock()
        repository.cache_manager = AsyncMock()

        result = await repository.update(dummy_mock, commit=True)
        self.assertIsNone(result)

        repository.entity_manager.update.assert_called_once_with(
            dummy_mock, commit=True)
        repository.cache_manager.delete.assert_called_once_with(dummy_mock)

    async def test__update_cacheable_commit_false(self):
        """Test update with cacheable entity and commit False."""
        dummy_class_mock = MagicMock(__tablename__="dummies", _cacheable=True)
        dummy_mock = MagicMock()

        repository = Repository(None, None, dummy_class_mock)
        repository.entity_manager = AsyncMock()
        repository.cache_manager = AsyncMock()

        result = await repository.update(dummy_mock, commit=False)
        self.assertIsNone(result)

        repository.entity_manager.update.assert_called_once_with(
            dummy_mock, commit=False)
        repository.cache_manager.delete.assert_called_once_with(dummy_mock)

    async def test__update_uncacheable_commit_true(self):
        """Test update with uncacheable entity and commit True."""
        dummy_class_mock = MagicMock(__tablename__="dummies", _cacheable=False)
        dummy_mock = MagicMock()

        repository = Repository(None, None, dummy_class_mock)
        repository.entity_manager = AsyncMock()
        repository.cache_manager = AsyncMock()

        result = await repository.update(dummy_mock, commit=True)
        self.assertIsNone(result)

        repository.entity_manager.update.assert_called_once_with(
            dummy_mock, commit=True)
        repository.cache_manager.set.assert_not_called()
        repository.cache_manager.delete.assert_not_called()

    async def test__update_uncacheable_commit_false(self):
        """Test update with uncacheable entity and commit False."""
        dummy_class_mock = MagicMock(__tablename__="dummies", _cacheable=False)
        dummy_mock = MagicMock()

        repository = Repository(None, None, dummy_class_mock)
        repository.entity_manager = AsyncMock()
        repository.cache_manager = AsyncMock()

        result = await repository.update(dummy_mock, commit=False)
        self.assertIsNone(result)

        repository.entity_manager.update.assert_called_once_with(
            dummy_mock, commit=False)
        repository.cache_manager.set.assert_not_called()
        repository.cache_manager.delete.assert_not_called()

    async def test__delete_cacheable_commit_true(self):
        """Test delete with cacheable entity and commit True."""
        dummy_class_mock = MagicMock(__tablename__="dummies", _cacheable=True)
        dummy_mock = MagicMock()

        repository = Repository(None, None, dummy_class_mock)
        repository.entity_manager = AsyncMock()
        repository.cache_manager = AsyncMock()

        result = await repository.delete(dummy_mock, commit=True)
        self.assertIsNone(result)

        repository.entity_manager.delete.assert_called_once_with(
            dummy_mock, commit=True)
        repository.cache_manager.delete.assert_called_once_with(dummy_mock)

    async def test__delete_cacheable_commit_false(self):
        """Test delete with cacheable entity and commit False."""
        dummy_class_mock = MagicMock(__tablename__="dummies", _cacheable=True)
        dummy_mock = MagicMock()

        repository = Repository(None, None, dummy_class_mock)
        repository.entity_manager = AsyncMock()
        repository.cache_manager = AsyncMock()

        result = await repository.delete(dummy_mock, commit=False)
        self.assertIsNone(result)

        repository.entity_manager.delete.assert_called_once_with(
            dummy_mock, commit=False)
        repository.cache_manager.delete.assert_called_once_with(dummy_mock)

    async def test__delete_uncacheable_commit_true(self):
        """Test delete with uncacheable entity and commit True."""
        dummy_class_mock = MagicMock(__tablename__="dummies", _cacheable=False)
        dummy_mock = MagicMock()

        repository = Repository(None, None, dummy_class_mock)
        repository.entity_manager = AsyncMock()
        repository.cache_manager = AsyncMock()

        result = await repository.delete(dummy_mock, commit=True)
        self.assertIsNone(result)

        repository.entity_manager.delete.assert_called_once_with(
            dummy_mock, commit=True)
        repository.cache_manager.delete.assert_not_called()

    async def test__delete_uncacheable_commit_false(self):
        """Test delete with uncacheable entity and commit False."""
        dummy_class_mock = MagicMock(__tablename__="dummies", _cacheable=False)
        dummy_mock = MagicMock()

        repository = Repository(None, None, dummy_class_mock)
        repository.entity_manager = AsyncMock()
        repository.cache_manager = AsyncMock()

        result = await repository.delete(dummy_mock, commit=False)
        self.assertIsNone(result)

        repository.entity_manager.delete.assert_called_once_with(
            dummy_mock, commit=False)
        repository.cache_manager.delete.assert_not_called()

    async def test__delete_all_from_cache_class_cacheable(self):
        dummy_class_mock = MagicMock(__tablename__="dummies", _cacheable=True)

        repository = Repository(None, None, dummy_class_mock)
        repository.entity_manager = AsyncMock()
        repository.cache_manager = AsyncMock()

        result = await repository.delete_all_from_cache()
        self.assertIsNone(result)

        repository.cache_manager.delete_all.assert_called_once_with(
            dummy_class_mock)

    async def test__delete_all_from_cache_class_not_cacheable(self):
        dummy_class_mock = MagicMock(__tablename__="dummies", _cacheable=False)

        repository = Repository(None, None, dummy_class_mock)
        repository.entity_manager = AsyncMock()
        repository.cache_manager = AsyncMock()

        result = await repository.delete_all_from_cache()
        self.assertIsNone(result)

        repository.cache_manager.delete_all.assert_not_called()

    async def test__count_all(self):
        """Test count_all method."""
        dummy_class_mock = MagicMock()
        dummies_count = 123

        repository = Repository(None, None, dummy_class_mock)
        repository.entity_manager = AsyncMock()
        repository.entity_manager.count_all.return_value = dummies_count

        result = await repository.count_all(key__eq="value")
        self.assertEqual(result, dummies_count)

        repository.entity_manager.count_all.assert_called_once_with(
            dummy_class_mock, key__eq="value")

    async def test__sum_all(self):
        """Test sum_all method."""
        dummy_class_mock = MagicMock()
        dummies_sum = 123

        repository = Repository(None, None, dummy_class_mock)
        repository.entity_manager = AsyncMock()
        repository.entity_manager.sum_all.return_value = dummies_sum

        result = await repository.sum_all("key", key__eq="value")
        self.assertEqual(result, dummies_sum)

        repository.entity_manager.sum_all.assert_called_once_with(
            dummy_class_mock, "key", key__eq="value")

    async def test__commit(self):
        """Test commit method."""
        repository = Repository(None, None, None)
        repository.entity_manager = AsyncMock()

        result = await repository.commit()
        self.assertIsNone(result)

        repository.entity_manager.commit.assert_called_once()

    async def test__rollback(self):
        """Test rollback method."""
        repository = Repository(None, None, None)
        repository.entity_manager = AsyncMock()

        result = await repository.rollback()
        self.assertIsNone(result)

        repository.entity_manager.rollback.assert_called_once()


if __name__ == "__main__":
    unittest.main()
