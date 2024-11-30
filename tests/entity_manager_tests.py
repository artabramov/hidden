"""
This module contains unit tests for the EntityManager class, which
manages database entity operations such as existence checks, insertion,
updates, and deletions. The tests cover a range of scenarios, including
various configurations for the flush and commit parameters, as well as
batch operations for deleting and counting records. The asynctest and
unittest libraries are used to validate that the EntityManager functions
correctly under different conditions, using mock objects to simulate
database interactions without requiring a real database.
"""

import asynctest
import unittest
from unittest.mock import MagicMock, AsyncMock, patch, call


class EntityManagerTestCase(asynctest.TestCase):
    """Unit tests for the EntityManager class."""

    async def setUp(self):
        """Set up the test case environment."""
        from app.managers.entity_manager import EntityManager

        self.session_mock = AsyncMock()
        self.entity_manager = EntityManager(self.session_mock)

    async def tearDown(self):
        """Clean up after each test."""
        del self.session_mock
        del self.entity_manager

    async def test__init(self):
        """Test the initialization of EntityManager."""
        self.assertEqual(self.entity_manager.session, self.session_mock)

    @patch("app.managers.entity_manager.EntityManager._where")
    @patch("app.managers.entity_manager.select")
    async def test__exists_true(self, select_mock, where_mock):
        """Test the exists method when the entity exists."""
        dummy_mock = MagicMock()
        dummy_class_mock = MagicMock()
        async_result_mock = MagicMock()
        async_result_mock.unique.return_value.scalars.return_value.one_or_none.return_value = dummy_mock # noqa E501
        self.session_mock.execute.return_value = async_result_mock
        kwargs = {"name__eq": "dummy"}

        result = await self.entity_manager.exists(dummy_class_mock, **kwargs)
        self.assertTrue(result)

        select_mock.assert_called_once_with(dummy_class_mock)
        where_mock.assert_called_once_with(dummy_class_mock, **kwargs)
        select_mock.return_value.where.assert_called_once_with(
            *where_mock.return_value)
        select_mock.return_value.where.return_value.limit.assert_called_once_with(1)  # noqa E501
        self.session_mock.execute.assert_called_once_with(
            select_mock.return_value.where.return_value.limit.return_value)
        async_result_mock.unique.return_value.scalars.return_value.one_or_none.assert_called_once() # noqa E501

    @patch("app.managers.entity_manager.EntityManager._where")
    @patch("app.managers.entity_manager.select")
    async def test__exists_false(self, select_mock, where_mock):
        """Test the exists method when the entity does not exist."""
        dummy_class_mock = MagicMock()
        async_result_mock = MagicMock()
        async_result_mock.unique.return_value.scalars.return_value.one_or_none.return_value = None # noqa E501
        self.session_mock.execute.return_value = async_result_mock
        kwargs = {"name__eq": "dummy"}

        result = await self.entity_manager.exists(dummy_class_mock, **kwargs)
        self.assertFalse(result)

        select_mock.assert_called_once_with(dummy_class_mock)
        where_mock.assert_called_once_with(dummy_class_mock, **kwargs)
        select_mock.return_value.where.assert_called_once_with(
            *where_mock.return_value)
        select_mock.return_value.where.return_value.limit.assert_called_once_with(1)  # noqa E501
        self.session_mock.execute.assert_called_once_with(
            select_mock.return_value.where.return_value.limit.return_value)
        async_result_mock.unique.return_value.scalars.return_value.one_or_none.assert_called_once() # noqa E501

    @patch("app.managers.entity_manager.EntityManager.flush")
    @patch("app.managers.entity_manager.EntityManager.commit")
    async def test__insert(self, commit_mock, flush_mock):
        """Test the insert method with default flush and commit."""
        dummy_mock = MagicMock()

        result = await self.entity_manager.insert(dummy_mock)
        self.assertIsNone(result)

        self.session_mock.add.assert_called_once_with(dummy_mock)
        flush_mock.assert_called_once()
        commit_mock.assert_called_once()

    @patch("app.managers.entity_manager.EntityManager.flush")
    @patch("app.managers.entity_manager.EntityManager.commit")
    async def test__insert_flush_true(self, commit_mock, flush_mock):
        """Test the insert method with flush set to True."""
        dummy_mock = MagicMock()

        result = await self.entity_manager.insert(dummy_mock, flush=True)
        self.assertIsNone(result)

        self.session_mock.add.assert_called_once_with(dummy_mock)
        flush_mock.assert_called_once()
        commit_mock.assert_called_once()

    @patch("app.managers.entity_manager.EntityManager.flush")
    @patch("app.managers.entity_manager.EntityManager.commit")
    async def test__insert_flush_false(self, commit_mock, flush_mock):
        """Test the insert method with flush set to False."""
        dummy_mock = MagicMock()

        result = await self.entity_manager.insert(dummy_mock, flush=False)
        self.assertIsNone(result)

        self.session_mock.add.assert_called_once_with(dummy_mock)
        flush_mock.assert_not_called()
        commit_mock.assert_called_once()

    @patch("app.managers.entity_manager.EntityManager.flush")
    @patch("app.managers.entity_manager.EntityManager.commit")
    async def test__insert_commit_true(self, commit_mock, flush_mock):
        """Test the insert method with commit set to True."""
        dummy_mock = MagicMock()

        result = await self.entity_manager.insert(dummy_mock, commit=True)
        self.assertIsNone(result)

        self.session_mock.add.assert_called_once_with(dummy_mock)
        flush_mock.assert_called_once()
        commit_mock.assert_called_once()

    @patch("app.managers.entity_manager.EntityManager.flush")
    @patch("app.managers.entity_manager.EntityManager.commit")
    async def test__insert_commit_false(self, commit_mock, flush_mock):
        """Test the insert method with commit set to False."""
        dummy_mock = MagicMock()

        result = await self.entity_manager.insert(dummy_mock, commit=False)
        self.assertIsNone(result)

        self.session_mock.add.assert_called_once_with(dummy_mock)
        flush_mock.assert_called_once()
        commit_mock.assert_not_called()

    @patch("app.managers.entity_manager.select")
    async def test__select(self, select_mock):
        """Test the select method for a specific ID."""
        dummy_mock = MagicMock(id=123)
        dummy_class_mock = MagicMock(id=123)
        async_result_mock = MagicMock()
        async_result_mock.unique.return_value.scalars.return_value.one_or_none.return_value = dummy_mock # noqa E501
        self.session_mock.execute.return_value = async_result_mock

        result = await self.entity_manager.select(dummy_class_mock, 123)
        self.assertEqual(result, dummy_mock)

        select_mock.assert_called_once_with(dummy_class_mock)
        select_mock.return_value.where.assert_called_once_with(True)
        select_mock.return_value.where.return_value.limit.assert_called_once_with(1)  # noqa E501
        async_result_mock.unique.return_value.scalars.return_value.one_or_none.assert_called_once() # noqa E501

    @patch("app.managers.entity_manager.EntityManager._where")
    @patch("app.managers.entity_manager.select")
    async def test__select_by(self, select_mock, where_mock):
        """Test the select_by method with specific criteria."""
        dummy_mock = MagicMock(key="dummy")
        dummy_class_mock = MagicMock()
        async_result_mock = MagicMock()
        async_result_mock.unique.return_value.scalars.return_value.one_or_none.return_value = dummy_mock # noqa E501
        self.session_mock.execute.return_value = async_result_mock

        result = await self.entity_manager.select_by(
            dummy_class_mock, key__eq="dummy")
        self.assertEqual(result, dummy_mock)

        select_mock.assert_called_once_with(dummy_class_mock)
        where_mock.assert_called_once_with(dummy_class_mock, key__eq="dummy")
        select_mock.return_value.where.assert_called_once_with(
            *where_mock.return_value)
        select_mock.return_value.where.return_value.limit.assert_called_once_with(1)  # noqa E501
        async_result_mock.unique.return_value.scalars.return_value.one_or_none.assert_called_once() # noqa E501

    @patch("app.managers.entity_manager.EntityManager._limit")
    @patch("app.managers.entity_manager.EntityManager._offset")
    @patch("app.managers.entity_manager.EntityManager._order_by")
    @patch("app.managers.entity_manager.EntityManager._where")
    @patch("app.managers.entity_manager.select")
    async def test__select_all(self, select_mock, where_mock, order_by_mock,
                               offset_mock, limit_mock):
        """Test the select_all method with multiple parameters."""
        dummy_mock = MagicMock()
        dummy_class_mock = MagicMock()
        async_result_mock = MagicMock()
        async_result_mock.unique.return_value.scalars.return_value.all.return_value = [dummy_mock] # noqa E501
        self.session_mock.execute.return_value = async_result_mock
        kwargs = {"name__eq": "dummy", "order_by": "id", "order": "asc",
                  "offset": 1, "limit": 2}

        result = await self.entity_manager.select_all(
            dummy_class_mock, **kwargs)
        self.assertListEqual(result, [dummy_mock])

        select_mock.assert_called_once_with(dummy_class_mock)
        where_mock.assert_called_once_with(dummy_class_mock, **kwargs)
        order_by_mock.assert_called_once_with(dummy_class_mock, **kwargs)
        offset_mock.assert_called_once_with(**kwargs)
        limit_mock.assert_called_once_with(**kwargs)
        select_mock.return_value.where.assert_called_once_with(
            *where_mock.return_value)
        select_mock.return_value.where.return_value.order_by.assert_called_once_with(order_by_mock.return_value) # noqa E501
        select_mock.return_value.where.return_value.order_by.return_value.offset.assert_called_once_with(offset_mock.return_value) # noqa E501
        select_mock.return_value.where.return_value.order_by.return_value.offset.return_value.limit.assert_called_once_with(limit_mock.return_value) # noqa E501
        select_mock.return_value.where.return_value.order_by.return_value.offset.return_value.limit.return_value.filter.assert_not_called()  # noqa E501
        dummy_class_mock.id.in_.assert_not_called()
        async_result_mock.unique.return_value.scalars.return_value.all.assert_called_once() # noqa E501

    @patch("app.managers.entity_manager.EntityManager._limit")
    @patch("app.managers.entity_manager.EntityManager._offset")
    @patch("app.managers.entity_manager.EntityManager._order_by")
    @patch("app.managers.entity_manager.EntityManager._where")
    @patch("app.managers.entity_manager.select")
    async def test__select_all_subquery(self, select_mock, where_mock,
                                        order_by_mock, offset_mock,
                                        limit_mock):
        """Test the select_all method with a subquery parameter."""
        dummy_mock = MagicMock()
        dummy_class_mock = MagicMock()
        async_result_mock = MagicMock()
        async_result_mock.unique.return_value.scalars.return_value.all.return_value = [dummy_mock] # noqa E501
        self.session_mock.execute.return_value = async_result_mock
        kwargs = {"name__eq": "dummy", "order_by": "id", "order": "asc",
                  "offset": 1, "limit": 2, "subquery": MagicMock()}

        result = await self.entity_manager.select_all(
            dummy_class_mock, **kwargs)
        self.assertListEqual(result, [dummy_mock])

        select_mock.assert_called_once_with(dummy_class_mock)
        where_mock.assert_called_once_with(dummy_class_mock, **kwargs)
        order_by_mock.assert_called_once_with(dummy_class_mock, **kwargs)
        offset_mock.assert_called_once_with(**kwargs)
        limit_mock.assert_called_once_with(**kwargs)
        select_mock.return_value.where.assert_called_once_with(
            *where_mock.return_value)
        select_mock.return_value.where.return_value.order_by.assert_called_once_with(order_by_mock.return_value) # noqa E501
        select_mock.return_value.where.return_value.order_by.return_value.offset.assert_called_once_with(offset_mock.return_value) # noqa E501
        select_mock.return_value.where.return_value.order_by.return_value.offset.return_value.limit.assert_called_once_with(limit_mock.return_value) # noqa E501
        select_mock.return_value.where.return_value.order_by.return_value.offset.return_value.limit.return_value.filter.assert_called_once_with(dummy_class_mock.id.in_.return_value)  # noqa E501
        dummy_class_mock.id.in_.assert_called_once()
        async_result_mock.unique.return_value.scalars.return_value.all.assert_called_once() # noqa E501

    @patch("app.managers.entity_manager.text")
    async def test__select_rows(self, text_mock):
        """Test the execute method."""
        execute_mock = MagicMock()
        execute_mock.fetchall.return_value = [('result',)]
        self.session_mock.execute.return_value = execute_mock
        sql = "SELECT 1;"

        result = await self.entity_manager.select_rows(sql)
        self.assertEqual(result, execute_mock.fetchall.return_value)

        self.session_mock.execute.assert_awaited_once_with(text_mock(sql))
        execute_mock.fetchall.assert_called_once()

    @patch("app.managers.entity_manager.EntityManager.flush")
    @patch("app.managers.entity_manager.EntityManager.commit")
    async def test__update(self, commit_mock, flush_mock):
        """Test the update method with default flush and commit."""
        dummy_mock = MagicMock()

        result = await self.entity_manager.update(dummy_mock)
        self.assertIsNone(result)

        self.session_mock.merge.assert_called_once_with(dummy_mock)
        flush_mock.assert_called_once()
        commit_mock.assert_not_called()

    @patch("app.managers.entity_manager.EntityManager.flush")
    @patch("app.managers.entity_manager.EntityManager.commit")
    async def test__update_flush_true(self, commit_mock, flush_mock):
        """Test the update method with flush set to True."""
        dummy_mock = MagicMock()

        result = await self.entity_manager.update(dummy_mock, flush=True)
        self.assertIsNone(result)

        self.session_mock.merge.assert_called_once_with(dummy_mock)
        flush_mock.assert_called_once()
        commit_mock.assert_not_called()

    @patch("app.managers.entity_manager.EntityManager.flush")
    @patch("app.managers.entity_manager.EntityManager.commit")
    async def test__update_flush_false(self, commit_mock, flush_mock):
        """Test the update method with flush set to False."""
        dummy_mock = MagicMock()

        result = await self.entity_manager.update(dummy_mock, flush=False)
        self.assertIsNone(result)

        self.session_mock.merge.assert_called_once_with(dummy_mock)
        flush_mock.assert_not_called()
        commit_mock.assert_not_called()

    @patch("app.managers.entity_manager.EntityManager.flush")
    @patch("app.managers.entity_manager.EntityManager.commit")
    async def test__update_commit_true(self, commit_mock, flush_mock):
        """Test the update method with commit set to True."""
        dummy_mock = MagicMock()

        result = await self.entity_manager.update(dummy_mock, commit=True)
        self.assertIsNone(result)

        self.session_mock.merge.assert_called_once_with(dummy_mock)
        flush_mock.assert_called_once()
        commit_mock.assert_called_once()

    @patch("app.managers.entity_manager.EntityManager.flush")
    @patch("app.managers.entity_manager.EntityManager.commit")
    async def test__update_commit_false(self, commit_mock, flush_mock):
        """Test the update method with commit set to False."""
        dummy_mock = MagicMock()

        result = await self.entity_manager.update(dummy_mock, commit=False)
        self.assertIsNone(result)

        self.session_mock.merge.assert_called_once_with(dummy_mock)
        flush_mock.assert_called_once()
        commit_mock.assert_not_called()

    @patch("app.managers.entity_manager.EntityManager.flush")
    @patch("app.managers.entity_manager.EntityManager.commit")
    async def test__delete(self, commit_mock, flush_mock):
        """Test the delete method with default commit."""
        dummy_mock = MagicMock()

        result = await self.entity_manager.delete(dummy_mock)
        self.assertIsNone(result)

        self.session_mock.delete.assert_called_once_with(dummy_mock)
        flush_mock.assert_called_once()
        commit_mock.assert_not_called()

    @patch("app.managers.entity_manager.EntityManager.flush")
    @patch("app.managers.entity_manager.EntityManager.commit")
    async def test__delete_flush_true(self, commit_mock, flush_mock):
        """Test the delete method with flush set to True."""
        dummy_mock = MagicMock()

        result = await self.entity_manager.delete(dummy_mock, flush=True)
        self.assertIsNone(result)

        self.session_mock.delete.assert_called_once_with(dummy_mock)
        flush_mock.assert_called_once()
        commit_mock.assert_not_called()

    @patch("app.managers.entity_manager.EntityManager.flush")
    @patch("app.managers.entity_manager.EntityManager.commit")
    async def test__delete_flush_false(self, commit_mock, flush_mock):
        """Test the delete method with flush set to False."""
        dummy_mock = MagicMock()

        result = await self.entity_manager.delete(dummy_mock, flush=False)
        self.assertIsNone(result)

        self.session_mock.delete.assert_called_once_with(dummy_mock)
        flush_mock.assert_not_called()
        commit_mock.assert_not_called()

    @patch("app.managers.entity_manager.EntityManager.flush")
    @patch("app.managers.entity_manager.EntityManager.commit")
    async def test__delete_commit_true(self, commit_mock, flush_mock):
        """Test the delete method with commit set to True."""
        dummy_mock = MagicMock()

        result = await self.entity_manager.delete(dummy_mock, commit=True)
        self.assertIsNone(result)

        self.session_mock.delete.assert_called_once_with(dummy_mock)
        flush_mock.assert_called_once()
        commit_mock.assert_called_once()

    @patch("app.managers.entity_manager.EntityManager.flush")
    @patch("app.managers.entity_manager.EntityManager.commit")
    async def test__delete_commit_false(self, commit_mock, flush_mock):
        """Test the delete method with commit set to False."""
        dummy_mock = MagicMock()

        result = await self.entity_manager.delete(dummy_mock, commit=False)
        self.assertIsNone(result)

        self.session_mock.delete.assert_called_once_with(dummy_mock)
        flush_mock.assert_called_once()
        commit_mock.assert_not_called()

    @patch("app.managers.entity_manager.EntityManager.delete")
    @patch("app.managers.entity_manager.EntityManager.select_all")
    async def test__delete_all(self, select_all_mock, delete_mock):
        """Test the delete_all method with default commit."""
        from app.managers.entity_manager import DELETE_ALL_BATCH_SIZE

        dummy_class_mock = MagicMock()
        entity_1, entity_2, entity_3 = MagicMock(), MagicMock(), MagicMock()
        select_all_mock.side_effect = [[entity_1, entity_2], [entity_3], []]

        result = await self.entity_manager.delete_all(
            dummy_class_mock, name__eq="dummy")
        self.assertIsNone(result)

        self.assertEqual(select_all_mock.call_count, 3)
        self.assertListEqual(select_all_mock.call_args_list, [
            call(dummy_class_mock, name__eq="dummy",
                 order_by="id", order="asc",
                 offset=0, limit=DELETE_ALL_BATCH_SIZE),
            call(dummy_class_mock, name__eq="dummy",
                 order_by="id", order="asc",
                 offset=DELETE_ALL_BATCH_SIZE, limit=DELETE_ALL_BATCH_SIZE),
            call(dummy_class_mock, name__eq="dummy",
                 order_by="id", order="asc",
                 offset=DELETE_ALL_BATCH_SIZE * 2,
                 limit=DELETE_ALL_BATCH_SIZE)])

        self.assertEqual(delete_mock.call_count, 3)
        self.assertListEqual(delete_mock.call_args_list, [
            call(entity_1, flush=True, commit=False),
            call(entity_2, flush=True, commit=False),
            call(entity_3, flush=True, commit=False),
        ])

    @patch("app.managers.entity_manager.EntityManager.delete")
    @patch("app.managers.entity_manager.EntityManager.select_all")
    async def test__delete_all_flush_true(self, select_all_mock, delete_mock):
        """Test the delete_all method with flush set to True."""
        from app.managers.entity_manager import DELETE_ALL_BATCH_SIZE

        dummy_class_mock = MagicMock()
        entity_1, entity_2, entity_3 = MagicMock(), MagicMock(), MagicMock()
        select_all_mock.side_effect = [[entity_1, entity_2], [entity_3], []]

        result = await self.entity_manager.delete_all(
            dummy_class_mock, flush=True, name__eq="dummy")
        self.assertIsNone(result)

        self.assertEqual(select_all_mock.call_count, 3)
        self.assertListEqual(select_all_mock.call_args_list, [
            call(dummy_class_mock, name__eq="dummy",
                 order_by="id", order="asc",
                 offset=0, limit=DELETE_ALL_BATCH_SIZE),
            call(dummy_class_mock, name__eq="dummy",
                 order_by="id", order="asc",
                 offset=DELETE_ALL_BATCH_SIZE, limit=DELETE_ALL_BATCH_SIZE),
            call(dummy_class_mock, name__eq="dummy",
                 order_by="id", order="asc",
                 offset=DELETE_ALL_BATCH_SIZE * 2,
                 limit=DELETE_ALL_BATCH_SIZE)])

        self.assertEqual(delete_mock.call_count, 3)
        self.assertListEqual(delete_mock.call_args_list, [
            call(entity_1, flush=True, commit=False),
            call(entity_2, flush=True, commit=False),
            call(entity_3, flush=True, commit=False),
        ])

    @patch("app.managers.entity_manager.EntityManager.delete")
    @patch("app.managers.entity_manager.EntityManager.select_all")
    async def test__delete_all_flush_false(self, select_all_mock, delete_mock):
        """Test the delete_all method with flush set to False."""
        from app.managers.entity_manager import DELETE_ALL_BATCH_SIZE

        dummy_class_mock = MagicMock()
        entity_1, entity_2, entity_3 = MagicMock(), MagicMock(), MagicMock()
        select_all_mock.side_effect = [[entity_1, entity_2], [entity_3], []]

        result = await self.entity_manager.delete_all(
            dummy_class_mock, flush=False, name__eq="dummy")
        self.assertIsNone(result)

        self.assertEqual(select_all_mock.call_count, 3)
        self.assertListEqual(select_all_mock.call_args_list, [
            call(dummy_class_mock, name__eq="dummy",
                 order_by="id", order="asc",
                 offset=0, limit=DELETE_ALL_BATCH_SIZE),
            call(dummy_class_mock, name__eq="dummy",
                 order_by="id", order="asc",
                 offset=DELETE_ALL_BATCH_SIZE, limit=DELETE_ALL_BATCH_SIZE),
            call(dummy_class_mock, name__eq="dummy",
                 order_by="id", order="asc",
                 offset=DELETE_ALL_BATCH_SIZE * 2,
                 limit=DELETE_ALL_BATCH_SIZE)])

        self.assertEqual(delete_mock.call_count, 3)
        self.assertListEqual(delete_mock.call_args_list, [
            call(entity_1, flush=False, commit=False),
            call(entity_2, flush=False, commit=False),
            call(entity_3, flush=False, commit=False),
        ])

    @patch("app.managers.entity_manager.EntityManager.delete")
    @patch("app.managers.entity_manager.EntityManager.select_all")
    async def test__delete_all_commit_true(self, select_all_mock, delete_mock):
        """Test the delete_all method with commit set to True."""
        from app.managers.entity_manager import DELETE_ALL_BATCH_SIZE

        dummy_class_mock = MagicMock()
        entity_1, entity_2, entity_3 = MagicMock(), MagicMock(), MagicMock()
        select_all_mock.side_effect = [[entity_1, entity_2], [entity_3], []]

        result = await self.entity_manager.delete_all(
            dummy_class_mock, commit=True, name__eq="dummy")
        self.assertIsNone(result)

        self.assertEqual(select_all_mock.call_count, 3)
        self.assertListEqual(select_all_mock.call_args_list, [
            call(dummy_class_mock, name__eq="dummy",
                 order_by="id", order="asc",
                 offset=0, limit=DELETE_ALL_BATCH_SIZE),
            call(dummy_class_mock, name__eq="dummy",
                 order_by="id", order="asc",
                 offset=DELETE_ALL_BATCH_SIZE, limit=DELETE_ALL_BATCH_SIZE),
            call(dummy_class_mock, name__eq="dummy",
                 order_by="id", order="asc",
                 offset=DELETE_ALL_BATCH_SIZE * 2,
                 limit=DELETE_ALL_BATCH_SIZE)])

        self.assertEqual(delete_mock.call_count, 3)
        self.assertListEqual(delete_mock.call_args_list, [
            call(entity_1, flush=True, commit=True),
            call(entity_2, flush=True, commit=True),
            call(entity_3, flush=True, commit=True),
        ])

    @patch("app.managers.entity_manager.EntityManager.delete")
    @patch("app.managers.entity_manager.EntityManager.select_all")
    async def test__delete_all_commit_false(self, select_all_mock,
                                            delete_mock):
        """Test the delete_all method with commit set to False."""
        from app.managers.entity_manager import DELETE_ALL_BATCH_SIZE

        dummy_class_mock = MagicMock()
        entity_1, entity_2, entity_3 = MagicMock(), MagicMock(), MagicMock()
        select_all_mock.side_effect = [[entity_1, entity_2], [entity_3], []]

        result = await self.entity_manager.delete_all(
            dummy_class_mock, commit=False, name__eq="dummy")
        self.assertIsNone(result)

        self.assertEqual(select_all_mock.call_count, 3)
        self.assertListEqual(select_all_mock.call_args_list, [
            call(dummy_class_mock, name__eq="dummy",
                 order_by="id", order="asc",
                 offset=0, limit=DELETE_ALL_BATCH_SIZE),
            call(dummy_class_mock, name__eq="dummy",
                 order_by="id", order="asc",
                 offset=DELETE_ALL_BATCH_SIZE, limit=DELETE_ALL_BATCH_SIZE),
            call(dummy_class_mock, name__eq="dummy",
                 order_by="id", order="asc",
                 offset=DELETE_ALL_BATCH_SIZE * 2,
                 limit=DELETE_ALL_BATCH_SIZE)])

        self.assertEqual(delete_mock.call_count, 3)
        self.assertListEqual(delete_mock.call_args_list, [
            call(entity_1, flush=True, commit=False),
            call(entity_2, flush=True, commit=False),
            call(entity_3, flush=True, commit=False),
        ])

    @patch("app.managers.entity_manager.EntityManager._where")
    @patch("app.managers.entity_manager.func")
    @patch("app.managers.entity_manager.select")
    async def test__count_all(self, select_mock, func_mock, where_mock):
        """Test the count_all method with criteria."""
        dummy_class_mock = MagicMock()
        async_result_mock = MagicMock()
        async_result_mock.unique.return_value.scalars.return_value.one_or_none.return_value = 123 # noqa E501
        self.session_mock.execute.return_value = async_result_mock
        kwargs = {"name__eq": "dummy"}

        result = await self.entity_manager.count_all(
            dummy_class_mock, **kwargs)
        self.assertEqual(result, 123)

        func_mock.count.assert_called_once_with(dummy_class_mock.id)
        where_mock.assert_called_once_with(dummy_class_mock, **kwargs)
        select_mock.assert_called_once_with(func_mock.count.return_value)
        select_mock.return_value.where.assert_called_once_with(
            *where_mock.return_value)
        select_mock.return_value.where.return_value.filter.assert_not_called()
        dummy_class_mock.id.in_.assert_not_called()
        async_result_mock.unique.return_value.scalars.return_value.one_or_none.assert_called_once() # noqa E501

    @patch("app.managers.entity_manager.EntityManager._where")
    @patch("app.managers.entity_manager.func")
    @patch("app.managers.entity_manager.select")
    async def test__count_all_subquery(self, select_mock, func_mock,
                                       where_mock):
        """Test the count_all method with a subquery parameter."""
        dummy_class_mock = MagicMock()
        async_result_mock = MagicMock()
        async_result_mock.unique.return_value.scalars.return_value.one_or_none.return_value = 123 # noqa E501
        self.session_mock.execute.return_value = async_result_mock
        kwargs = {"name__eq": "dummy", "subquery": MagicMock()}

        result = await self.entity_manager.count_all(
            dummy_class_mock, **kwargs)
        self.assertEqual(result, 123)

        func_mock.count.assert_called_once_with(dummy_class_mock.id)
        where_mock.assert_called_once_with(dummy_class_mock, **kwargs)
        select_mock.assert_called_once_with(func_mock.count.return_value)
        select_mock.return_value.where.assert_called_once_with(
            *where_mock.return_value)
        select_mock.return_value.where.return_value.filter.assert_called_once_with(dummy_class_mock.id.in_.return_value)  # noqa E501
        dummy_class_mock.id.in_.assert_called_once()
        async_result_mock.unique.return_value.scalars.return_value.one_or_none.assert_called_once() # noqa E501

    @patch("app.managers.entity_manager.EntityManager._where")
    @patch("app.managers.entity_manager.func")
    @patch("app.managers.entity_manager.select")
    async def test__count_all_none(self, select_mock, func_mock, where_mock):
        """Test the count_all method when no records are found."""
        dummy_class_mock = MagicMock(id=1)
        async_result_mock = MagicMock()
        async_result_mock.unique.return_value.scalars.return_value.one_or_none.return_value = None # noqa E501
        self.session_mock.execute.return_value = async_result_mock
        kwargs = {"name__eq": "dummy"}

        result = await self.entity_manager.count_all(
            dummy_class_mock, **kwargs)
        self.assertEqual(result, 0)

        func_mock.count.assert_called_once_with(dummy_class_mock.id)
        where_mock.assert_called_once_with(dummy_class_mock, **kwargs)
        select_mock.assert_called_once_with(func_mock.count.return_value)
        select_mock.return_value.where.assert_called_once_with(
            *where_mock.return_value)
        async_result_mock.unique.return_value.scalars.return_value.one_or_none.assert_called_once() # noqa E501

    @patch("app.managers.entity_manager.EntityManager._where")
    @patch("app.managers.entity_manager.func")
    @patch("app.managers.entity_manager.select")
    async def test__sum_all(self, select_mock, func_mock, where_mock):
        """Test the sum_all method with criteria."""
        dummy_class_mock = MagicMock(name="dummy", number=1)
        async_result_mock = MagicMock()
        async_result_mock.unique.return_value.scalars.return_value.one_or_none.return_value = 123 # noqa E501
        self.session_mock.execute.return_value = async_result_mock
        kwargs = {"name__eq": "dummy"}

        result = await self.entity_manager.sum_all(
            dummy_class_mock, "number", **kwargs)
        self.assertEqual(result, 123)

        func_mock.sum.assert_called_once_with(dummy_class_mock.number)
        where_mock.assert_called_once_with(dummy_class_mock, **kwargs)
        select_mock.assert_called_once_with(func_mock.sum.return_value)
        select_mock.return_value.where.assert_called_once_with(
            *where_mock.return_value)
        select_mock.return_value.where.return_value.filter.assert_not_called()
        dummy_class_mock.id.in_.assert_not_called()
        async_result_mock.unique.return_value.scalars.return_value.one_or_none.assert_called_once() # noqa E501

    @patch("app.managers.entity_manager.EntityManager._where")
    @patch("app.managers.entity_manager.func")
    @patch("app.managers.entity_manager.select")
    async def test__sum_all_subquery(self, select_mock, func_mock, where_mock):
        """Test the sum_all method with a subquery parameter."""
        dummy_class_mock = MagicMock(name="dummy", number=1)
        async_result_mock = MagicMock()
        async_result_mock.unique.return_value.scalars.return_value.one_or_none.return_value = 123 # noqa E501
        self.session_mock.execute.return_value = async_result_mock
        kwargs = {"name__eq": "dummy", "subquery": MagicMock()}

        result = await self.entity_manager.sum_all(
            dummy_class_mock, "number", **kwargs)
        self.assertEqual(result, 123)

        func_mock.sum.assert_called_once_with(dummy_class_mock.number)
        where_mock.assert_called_once_with(dummy_class_mock, **kwargs)
        select_mock.assert_called_once_with(func_mock.sum.return_value)
        select_mock.return_value.where.assert_called_once_with(
            *where_mock.return_value)
        select_mock.return_value.where.return_value.filter.assert_called_once_with(  # noqa E501
            dummy_class_mock.id.in_.return_value)
        dummy_class_mock.id.in_.assert_called_once()
        async_result_mock.unique.return_value.scalars.return_value.one_or_none.assert_called_once() # noqa E501

    @patch("app.managers.entity_manager.EntityManager._where")
    @patch("app.managers.entity_manager.func")
    @patch("app.managers.entity_manager.select")
    async def test__sum_all_none(self, select_mock, func_mock, where_mock):
        """Test the sum_all method when no records are found."""
        dummy_class_mock = MagicMock(name="dummy", number=1)
        async_result_mock = MagicMock()
        async_result_mock.unique.return_value.scalars.return_value.one_or_none.return_value = None # noqa E501
        self.session_mock.execute.return_value = async_result_mock
        kwargs = {"name__eq": "dummy"}

        result = await self.entity_manager.sum_all(dummy_class_mock, "number",
                                                   **kwargs)
        self.assertEqual(result, 0)

        func_mock.sum.assert_called_once_with(dummy_class_mock.number)
        where_mock.assert_called_once_with(dummy_class_mock, **kwargs)
        select_mock.assert_called_once_with(func_mock.sum.return_value)
        select_mock.return_value.where.assert_called_once_with(
            *where_mock.return_value)
        async_result_mock.unique.return_value.scalars.return_value.one_or_none.assert_called_once() # noqa E501

    @patch("app.managers.entity_manager.select")
    async def test__subquery(self, select_mock):
        """Test the subquery method in entity_manager."""
        class_mock = MagicMock(dummy_id="class_column")
        foreign_key = "dummy_id"
        kwargs = {"key__eq": "value"}

        result = await self.entity_manager.subquery(
            class_mock, foreign_key, **kwargs)
        self.assertTrue(isinstance(result, MagicMock))

        select_mock.assert_called_once_with(class_mock.dummy_id)
        select_mock.return_value.filter.assert_called_once()
        select_mock.return_value.filter.return_value.subquery.assert_called_once()  # noqa E501

    async def test__flush(self):
        """Test the flush method."""
        result = await self.entity_manager.flush()
        self.assertIsNone(result)
        self.session_mock.flush.assert_called_once()

    async def test__commit(self):
        """Test the commit method."""
        result = await self.entity_manager.commit()
        self.assertIsNone(result)
        self.session_mock.commit.assert_called_once()

    async def test__rollback(self):
        """Test the rollback method."""
        result = await self.entity_manager.rollback()
        self.assertIsNone(result)
        self.session_mock.rollback.assert_called_once()

    async def test__where(self):
        """Test the _where method for generating SQL conditions."""
        (in_mock, eq_mock, ne_mock, ge_mock, le_mock, gt_mock, lt_mock,
         like_mock, ilike_mock) = (
            MagicMock(), MagicMock(), MagicMock(), MagicMock(), MagicMock(),
            MagicMock(), MagicMock(), MagicMock(), MagicMock())
        column_mock = MagicMock(
            in_=in_mock, __eq__=eq_mock, __ne__=ne_mock, __ge__=ge_mock,
            __le__=le_mock, __gt__=gt_mock, __lt__=lt_mock, like=like_mock,
            ilike=ilike_mock)
        dummy_class_mock = MagicMock(column=column_mock)
        kwargs = {
            "column__in": "1, 2",
            "column__eq": "3",
            "column__ne": "4",
            "column__ge": "5",
            "column__le": "6",
            "column__gt": "7",
            "column__lt": "8",
            "column__like": "dummy",
            "column__ilike": "dummy",
        }

        result = self.entity_manager._where(dummy_class_mock, **kwargs)
        self.assertListEqual(result, [
            in_mock.return_value,
            eq_mock.return_value,
            ne_mock.return_value,
            ge_mock.return_value,
            le_mock.return_value,
            gt_mock.return_value,
            lt_mock.return_value,
            like_mock.return_value,
            ilike_mock.return_value,
        ])

        in_mock.assert_called_once_with([
            x.strip() for x in kwargs["column__in"].split(",")])
        eq_mock.assert_called_once_with(kwargs["column__eq"])
        ne_mock.assert_called_once_with(kwargs["column__ne"])
        ge_mock.assert_called_once_with(kwargs["column__ge"])
        le_mock.assert_called_once_with(kwargs["column__le"])
        gt_mock.assert_called_once_with(kwargs["column__gt"])
        lt_mock.assert_called_once_with(kwargs["column__lt"])
        like_mock.assert_called_once_with("%" + kwargs["column__like"] + "%")
        ilike_mock.assert_called_once_with("%" + kwargs["column__ilike"] + "%")

    @patch("app.managers.entity_manager.asc")
    async def test__order_by_asc(self, asc_mock):
        """Test the _order_by method for ascending order."""
        column_mock = MagicMock()
        dummy_class_mock = MagicMock(column=column_mock)
        kwargs = {"order_by": "column", "order": "asc"}
        result = self.entity_manager._order_by(dummy_class_mock, **kwargs)

        self.assertEqual(result, asc_mock.return_value)
        asc_mock.assert_called_once_with(column_mock)

    @patch("app.managers.entity_manager.desc")
    async def test__order_by_desc(self, desc_mock):
        """Test _order_by with descending order."""
        column_mock = MagicMock()
        dummy_class_mock = MagicMock(column=column_mock)
        kwargs = {"order_by": "column", "order": "desc"}

        result = self.entity_manager._order_by(dummy_class_mock, **kwargs)
        self.assertEqual(result, desc_mock.return_value)

        desc_mock.assert_called_once_with(column_mock)

    @patch("app.managers.entity_manager.func")
    async def test__order_by_rand(self, func_mock):
        """Test _order_by with random order."""
        column_mock = MagicMock()
        dummy_class_mock = MagicMock(column=column_mock)
        kwargs = {"order_by": "column", "order": "rand"}

        result = self.entity_manager._order_by(dummy_class_mock, **kwargs)
        self.assertEqual(result, func_mock.random.return_value)

    async def test__offset(self):
        """Test _offset method returns the offset value."""
        kwargs = {"offset": 123}
        result = self.entity_manager._offset(**kwargs)
        self.assertEqual(result, 123)

    async def test__limit(self):
        """Test _limit method returns the limit value."""
        kwargs = {"limit": 123}
        result = self.entity_manager._limit(**kwargs)
        self.assertEqual(result, 123)


if __name__ == "__main__":
    unittest.main()
