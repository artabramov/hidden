import unittest
from unittest.mock import MagicMock, AsyncMock, patch, call
from app.managers.entity_manager import EntityManager, DELETE_ALL_BATCH_SIZE


class EntityManagerTest(unittest.IsolatedAsyncioTestCase):

    async def test_init(self):
        session_mock = MagicMock()
        entity_manager = EntityManager(session_mock)

        self.assertEqual(entity_manager.session, session_mock)

    @patch("app.managers.entity_manager.EntityManager._where")
    @patch("app.managers.entity_manager.select")
    async def test_exists_true(self, select_mock, where_mock):
        session_mock = AsyncMock()
        entity_manager = EntityManager(session_mock)
        obj_mock = MagicMock()
        cls_mock = MagicMock()

        result_mock = MagicMock()
        result_mock.unique.return_value.scalars.return_value.one_or_none.return_value = obj_mock # noqa E501

        session_mock.execute.return_value = result_mock
        kwargs = {"name__eq": "name"}

        result = await entity_manager.exists(cls_mock, **kwargs)
        self.assertTrue(result)

        select_mock.assert_called_once_with(cls_mock)
        where_mock.assert_called_once_with(cls_mock, **kwargs)

        select_mock.return_value.where.assert_called_once_with(
            *where_mock.return_value)

        select_mock.return_value.where.return_value.limit.assert_called_once_with(1)  # noqa E501

        session_mock.execute.assert_called_once_with(
            select_mock.return_value.where.return_value.limit.return_value)
        result_mock.unique.return_value.scalars.return_value.one_or_none.assert_called_once() # noqa E501

    @patch("app.managers.entity_manager.EntityManager._where")
    @patch("app.managers.entity_manager.select")
    async def test_exists_false(self, select_mock, where_mock):
        session_mock = AsyncMock()
        entity_manager = EntityManager(session_mock)
        cls_mock = MagicMock()

        result_mock = MagicMock()
        result_mock.unique.return_value.scalars.return_value.one_or_none.return_value = None # noqa E501

        session_mock.execute.return_value = result_mock
        kwargs = {"name__eq": "name"}

        result = await entity_manager.exists(cls_mock, **kwargs)
        self.assertFalse(result)

        select_mock.assert_called_once_with(cls_mock)
        where_mock.assert_called_once_with(cls_mock, **kwargs)

        select_mock.return_value.where.assert_called_once_with(
            *where_mock.return_value)

        select_mock.return_value.where.return_value.limit.assert_called_once_with(1)  # noqa E501

        session_mock.execute.assert_called_once_with(
            select_mock.return_value.where.return_value.limit.return_value)
        result_mock.unique.return_value.scalars.return_value.one_or_none.assert_called_once() # noqa E501

    @patch("app.managers.entity_manager.EntityManager.flush")
    @patch("app.managers.entity_manager.EntityManager.commit")
    async def test_insert(self, commit_mock, flush_mock):
        session_mock = MagicMock()
        entity_manager = EntityManager(session_mock)
        obj_mock = AsyncMock()

        result = await entity_manager.insert(obj_mock)
        self.assertIsNone(result)

        session_mock.add.assert_called_once_with(obj_mock)
        flush_mock.assert_called_once()
        commit_mock.assert_called_once()

    @patch("app.managers.entity_manager.EntityManager.flush")
    @patch("app.managers.entity_manager.EntityManager.commit")
    async def test_insert_flush_true(self, commit_mock, flush_mock):
        session_mock = MagicMock()
        entity_manager = EntityManager(session_mock)
        obj_mock = MagicMock()

        result = await entity_manager.insert(obj_mock, flush=True)
        self.assertIsNone(result)

        session_mock.add.assert_called_once_with(obj_mock)
        flush_mock.assert_called_once()
        commit_mock.assert_called_once()

    @patch("app.managers.entity_manager.EntityManager.flush")
    @patch("app.managers.entity_manager.EntityManager.commit")
    async def test_insert_flush_false(self, commit_mock, flush_mock):
        session_mock = MagicMock()
        entity_manager = EntityManager(session_mock)
        obj_mock = MagicMock()

        result = await entity_manager.insert(obj_mock, flush=False)
        self.assertIsNone(result)

        session_mock.add.assert_called_once_with(obj_mock)
        flush_mock.assert_not_called()
        commit_mock.assert_called_once()

    @patch("app.managers.entity_manager.EntityManager.flush")
    @patch("app.managers.entity_manager.EntityManager.commit")
    async def test_insert_commit_true(self, commit_mock, flush_mock):
        session_mock = MagicMock()
        entity_manager = EntityManager(session_mock)
        obj_mock = MagicMock()

        result = await entity_manager.insert(obj_mock, commit=True)
        self.assertIsNone(result)

        session_mock.add.assert_called_once_with(obj_mock)
        flush_mock.assert_called_once()
        commit_mock.assert_called_once()

    @patch("app.managers.entity_manager.EntityManager.flush")
    @patch("app.managers.entity_manager.EntityManager.commit")
    async def test_insert_commit_false(self, commit_mock, flush_mock):
        session_mock = MagicMock()
        entity_manager = EntityManager(session_mock)
        obj_mock = MagicMock()

        result = await entity_manager.insert(obj_mock, commit=False)
        self.assertIsNone(result)

        session_mock.add.assert_called_once_with(obj_mock)
        flush_mock.assert_called_once()
        commit_mock.assert_not_called()

    @patch("app.managers.entity_manager.select")
    async def test_select(self, select_mock):
        session_mock = AsyncMock()
        entity_manager = EntityManager(session_mock)

        obj_mock = MagicMock(id=123)
        cls_mock = MagicMock(id=123)
        result_mock = MagicMock()

        result_mock.unique.return_value.scalars.return_value.one_or_none.return_value = obj_mock # noqa E501
        session_mock.execute.return_value = result_mock

        result = await entity_manager.select(cls_mock, 123)
        self.assertEqual(result, obj_mock)

        select_mock.assert_called_once_with(cls_mock)
        select_mock.return_value.where.assert_called_once_with(True)
        select_mock.return_value.where.return_value.limit.assert_called_once_with(1)  # noqa E501
        result_mock.unique.return_value.scalars.return_value.one_or_none.assert_called_once() # noqa E501

    @patch("app.managers.entity_manager.EntityManager._where")
    @patch("app.managers.entity_manager.select")
    async def test_select_by(self, select_mock, where_mock):
        session_mock = AsyncMock()
        entity_manager = EntityManager(session_mock)

        obj_mock = MagicMock(name="name")
        cls_mock = MagicMock()
        result_mock = MagicMock()

        result_mock.unique.return_value.scalars.return_value.one_or_none.return_value = obj_mock # noqa E501
        session_mock.execute.return_value = result_mock

        result = await entity_manager.select_by(cls_mock, name__eq="name")
        self.assertEqual(result, obj_mock)

        select_mock.assert_called_once_with(cls_mock)
        where_mock.assert_called_once_with(cls_mock, name__eq="name")
        select_mock.return_value.where.assert_called_once_with(
            *where_mock.return_value)
        select_mock.return_value.where.return_value.limit.assert_called_once_with(1)  # noqa E501
        result_mock.unique.return_value.scalars.return_value.one_or_none.assert_called_once() # noqa E501

    @patch("app.managers.entity_manager.EntityManager._limit")
    @patch("app.managers.entity_manager.EntityManager._offset")
    @patch("app.managers.entity_manager.EntityManager._order_by")
    @patch("app.managers.entity_manager.EntityManager._where")
    @patch("app.managers.entity_manager.select")
    async def test_select_all(self, select_mock, where_mock, order_by_mock,
                              offset_mock, limit_mock):
        session_mock = AsyncMock()
        entity_manager = EntityManager(session_mock)

        obj_mock = MagicMock()
        cls_mock = MagicMock()
        result_mock = MagicMock()
        result_mock.unique.return_value.scalars.return_value.all.return_value = [obj_mock] # noqa E501
        session_mock.execute.return_value = result_mock
        kwargs = {"name__eq": "dummy", "order_by": "id", "order": "asc",
                  "offset": 1, "limit": 2}

        result = await entity_manager.select_all(
            cls_mock, **kwargs)
        self.assertListEqual(result, [obj_mock])

        select_mock.assert_called_once_with(cls_mock)
        where_mock.assert_called_once_with(cls_mock, **kwargs)
        order_by_mock.assert_called_once_with(cls_mock, **kwargs)
        offset_mock.assert_called_once_with(**kwargs)
        limit_mock.assert_called_once_with(**kwargs)
        select_mock.return_value.where.assert_called_once_with(
            *where_mock.return_value)
        select_mock.return_value.where.return_value.order_by.assert_called_once_with(order_by_mock.return_value) # noqa E501
        select_mock.return_value.where.return_value.order_by.return_value.offset.assert_called_once_with(offset_mock.return_value) # noqa E501
        select_mock.return_value.where.return_value.order_by.return_value.offset.return_value.limit.assert_called_once_with(limit_mock.return_value) # noqa E501
        select_mock.return_value.where.return_value.order_by.return_value.offset.return_value.limit.return_value.filter.assert_not_called()  # noqa E501
        cls_mock.id.in_.assert_not_called()
        result_mock.unique.return_value.scalars.return_value.all.assert_called_once() # noqa E501

    @patch("app.managers.entity_manager.EntityManager._limit")
    @patch("app.managers.entity_manager.EntityManager._offset")
    @patch("app.managers.entity_manager.EntityManager._order_by")
    @patch("app.managers.entity_manager.EntityManager._where")
    @patch("app.managers.entity_manager.select")
    async def test_select_all_subquery(
            self, select_mock, where_mock, order_by_mock, offset_mock,
            limit_mock):
        session_mock = AsyncMock()
        entity_manager = EntityManager(session_mock)

        obj_mock = MagicMock()
        cls_mock = MagicMock()
        result_mock = MagicMock()
        result_mock.unique.return_value.scalars.return_value.all.return_value = [obj_mock] # noqa E501
        session_mock.execute.return_value = result_mock
        kwargs = {"name__eq": "dummy", "order_by": "id", "order": "asc",
                  "offset": 1, "limit": 2, "subquery": MagicMock()}

        result = await entity_manager.select_all(
            cls_mock, **kwargs)
        self.assertListEqual(result, [obj_mock])

        select_mock.assert_called_once_with(cls_mock)
        where_mock.assert_called_once_with(cls_mock, **kwargs)
        order_by_mock.assert_called_once_with(cls_mock, **kwargs)
        offset_mock.assert_called_once_with(**kwargs)
        limit_mock.assert_called_once_with(**kwargs)
        select_mock.return_value.where.assert_called_once_with(
            *where_mock.return_value)
        select_mock.return_value.where.return_value.order_by.assert_called_once_with(order_by_mock.return_value) # noqa E501
        select_mock.return_value.where.return_value.order_by.return_value.offset.assert_called_once_with(offset_mock.return_value) # noqa E501
        select_mock.return_value.where.return_value.order_by.return_value.offset.return_value.limit.assert_called_once_with(limit_mock.return_value) # noqa E501
        select_mock.return_value.where.return_value.order_by.return_value.offset.return_value.limit.return_value.filter.assert_called_once_with(cls_mock.id.in_.return_value)  # noqa E501
        cls_mock.id.in_.assert_called_once()
        result_mock.unique.return_value.scalars.return_value.all.assert_called_once() # noqa E501

    @patch("app.managers.entity_manager.text")
    async def test_select_rows(self, text_mock):
        session_mock = AsyncMock()
        entity_manager = EntityManager(session_mock)

        execute_mock = MagicMock()
        execute_mock.fetchall.return_value = [('result',)]
        session_mock.execute.return_value = execute_mock
        sql = "SELECT 1;"

        result = await entity_manager.select_rows(sql)
        self.assertEqual(result, execute_mock.fetchall.return_value)

        session_mock.execute.assert_awaited_once_with(text_mock(sql))
        execute_mock.fetchall.assert_called_once()

    @patch("app.managers.entity_manager.EntityManager.flush")
    @patch("app.managers.entity_manager.EntityManager.commit")
    async def test_update(self, commit_mock, flush_mock):
        session_mock = AsyncMock()
        entity_manager = EntityManager(session_mock)
        obj_mock = MagicMock()

        result = await entity_manager.update(obj_mock)
        self.assertIsNone(result)

        session_mock.merge.assert_called_once_with(obj_mock)
        flush_mock.assert_called_once()
        commit_mock.assert_not_called()

    @patch("app.managers.entity_manager.EntityManager.flush")
    @patch("app.managers.entity_manager.EntityManager.commit")
    async def test_update_flush_true(self, commit_mock, flush_mock):
        session_mock = AsyncMock()
        entity_manager = EntityManager(session_mock)
        obj_mock = MagicMock()

        result = await entity_manager.update(obj_mock, flush=True)
        self.assertIsNone(result)

        session_mock.merge.assert_called_once_with(obj_mock)
        flush_mock.assert_called_once()
        commit_mock.assert_not_called()

    @patch("app.managers.entity_manager.EntityManager.flush")
    @patch("app.managers.entity_manager.EntityManager.commit")
    async def test_update_flush_false(self, commit_mock, flush_mock):
        session_mock = AsyncMock()
        entity_manager = EntityManager(session_mock)
        obj_mock = MagicMock()

        result = await entity_manager.update(obj_mock, flush=False)
        self.assertIsNone(result)

        session_mock.merge.assert_called_once_with(obj_mock)
        flush_mock.assert_not_called()
        commit_mock.assert_not_called()

    @patch("app.managers.entity_manager.EntityManager.flush")
    @patch("app.managers.entity_manager.EntityManager.commit")
    async def test_update_commit_true(self, commit_mock, flush_mock):
        session_mock = AsyncMock()
        entity_manager = EntityManager(session_mock)
        obj_mock = MagicMock()

        result = await entity_manager.update(obj_mock, commit=True)
        self.assertIsNone(result)

        session_mock.merge.assert_called_once_with(obj_mock)
        flush_mock.assert_called_once()
        commit_mock.assert_called_once()

    @patch("app.managers.entity_manager.EntityManager.flush")
    @patch("app.managers.entity_manager.EntityManager.commit")
    async def test_update_commit_false(self, commit_mock, flush_mock):
        session_mock = AsyncMock()
        entity_manager = EntityManager(session_mock)
        obj_mock = MagicMock()

        result = await entity_manager.update(obj_mock, commit=False)
        self.assertIsNone(result)

        session_mock.merge.assert_called_once_with(obj_mock)
        flush_mock.assert_called_once()
        commit_mock.assert_not_called()

    @patch("app.managers.entity_manager.EntityManager.flush")
    @patch("app.managers.entity_manager.EntityManager.commit")
    async def test_delete(self, commit_mock, flush_mock):
        session_mock = AsyncMock()
        entity_manager = EntityManager(session_mock)
        obj_mock = MagicMock()

        result = await entity_manager.delete(obj_mock)
        self.assertIsNone(result)

        session_mock.delete.assert_called_once_with(obj_mock)
        flush_mock.assert_called_once()
        commit_mock.assert_not_called()

    @patch("app.managers.entity_manager.EntityManager.flush")
    @patch("app.managers.entity_manager.EntityManager.commit")
    async def test_delete_flush_true(self, commit_mock, flush_mock):
        session_mock = AsyncMock()
        entity_manager = EntityManager(session_mock)
        obj_mock = MagicMock()

        result = await entity_manager.delete(obj_mock, flush=True)
        self.assertIsNone(result)

        session_mock.delete.assert_called_once_with(obj_mock)
        flush_mock.assert_called_once()
        commit_mock.assert_not_called()

    @patch("app.managers.entity_manager.EntityManager.flush")
    @patch("app.managers.entity_manager.EntityManager.commit")
    async def test_delete_flush_false(self, commit_mock, flush_mock):
        session_mock = AsyncMock()
        entity_manager = EntityManager(session_mock)
        obj_mock = MagicMock()

        result = await entity_manager.delete(obj_mock, flush=False)
        self.assertIsNone(result)

        session_mock.delete.assert_called_once_with(obj_mock)
        flush_mock.assert_not_called()
        commit_mock.assert_not_called()

    @patch("app.managers.entity_manager.EntityManager.flush")
    @patch("app.managers.entity_manager.EntityManager.commit")
    async def test_delete_commit_true(self, commit_mock, flush_mock):
        session_mock = AsyncMock()
        entity_manager = EntityManager(session_mock)
        obj_mock = MagicMock()

        result = await entity_manager.delete(obj_mock, commit=True)
        self.assertIsNone(result)

        session_mock.delete.assert_called_once_with(obj_mock)
        flush_mock.assert_called_once()
        commit_mock.assert_called_once()

    @patch("app.managers.entity_manager.EntityManager.flush")
    @patch("app.managers.entity_manager.EntityManager.commit")
    async def test_delete_commit_false(self, commit_mock, flush_mock):
        session_mock = AsyncMock()
        entity_manager = EntityManager(session_mock)
        obj_mock = MagicMock()

        result = await entity_manager.delete(obj_mock, commit=False)
        self.assertIsNone(result)

        session_mock.delete.assert_called_once_with(obj_mock)
        flush_mock.assert_called_once()
        commit_mock.assert_not_called()

    @patch("app.managers.entity_manager.EntityManager.delete")
    @patch("app.managers.entity_manager.EntityManager.select_all")
    async def test_delete_all(self, select_all_mock, delete_mock):
        session_mock = AsyncMock()
        entity_manager = EntityManager(session_mock)

        cls_mock = MagicMock()
        entity_1, entity_2, entity_3 = MagicMock(), MagicMock(), MagicMock()
        select_all_mock.side_effect = [[entity_1, entity_2], [entity_3], []]

        result = await entity_manager.delete_all(cls_mock, name__eq="name")
        self.assertIsNone(result)

        self.assertEqual(select_all_mock.call_count, 3)
        self.assertListEqual(select_all_mock.call_args_list, [
            call(cls_mock, name__eq="name",
                 order_by="id", order="asc",
                 offset=0, limit=DELETE_ALL_BATCH_SIZE),
            call(cls_mock, name__eq="name",
                 order_by="id", order="asc",
                 offset=DELETE_ALL_BATCH_SIZE, limit=DELETE_ALL_BATCH_SIZE),
            call(cls_mock, name__eq="name",
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
    async def test_delete_all_flush_true(self, select_all_mock, delete_mock):
        session_mock = AsyncMock()
        entity_manager = EntityManager(session_mock)

        cls_mock = MagicMock()
        entity_1, entity_2, entity_3 = MagicMock(), MagicMock(), MagicMock()
        select_all_mock.side_effect = [[entity_1, entity_2], [entity_3], []]

        result = await entity_manager.delete_all(
            cls_mock, flush=True, name__eq="dummy")
        self.assertIsNone(result)

        self.assertEqual(select_all_mock.call_count, 3)
        self.assertListEqual(select_all_mock.call_args_list, [
            call(cls_mock, name__eq="dummy",
                 order_by="id", order="asc",
                 offset=0, limit=DELETE_ALL_BATCH_SIZE),
            call(cls_mock, name__eq="dummy",
                 order_by="id", order="asc",
                 offset=DELETE_ALL_BATCH_SIZE, limit=DELETE_ALL_BATCH_SIZE),
            call(cls_mock, name__eq="dummy",
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
    async def test_delete_all_flush_false(self, select_all_mock, delete_mock):
        session_mock = AsyncMock()
        entity_manager = EntityManager(session_mock)

        cls_mock = MagicMock()
        entity_1, entity_2, entity_3 = MagicMock(), MagicMock(), MagicMock()
        select_all_mock.side_effect = [[entity_1, entity_2], [entity_3], []]

        result = await entity_manager.delete_all(
            cls_mock, flush=False, name__eq="dummy")
        self.assertIsNone(result)

        self.assertEqual(select_all_mock.call_count, 3)
        self.assertListEqual(select_all_mock.call_args_list, [
            call(cls_mock, name__eq="dummy",
                 order_by="id", order="asc",
                 offset=0, limit=DELETE_ALL_BATCH_SIZE),
            call(cls_mock, name__eq="dummy",
                 order_by="id", order="asc",
                 offset=DELETE_ALL_BATCH_SIZE, limit=DELETE_ALL_BATCH_SIZE),
            call(cls_mock, name__eq="dummy",
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
    async def test_delete_all_commit_true(self, select_all_mock, delete_mock):
        session_mock = AsyncMock()
        entity_manager = EntityManager(session_mock)

        cls_mock = MagicMock()
        entity_1, entity_2, entity_3 = MagicMock(), MagicMock(), MagicMock()
        select_all_mock.side_effect = [[entity_1, entity_2], [entity_3], []]

        result = await entity_manager.delete_all(
            cls_mock, commit=True, name__eq="dummy")
        self.assertIsNone(result)

        self.assertEqual(select_all_mock.call_count, 3)
        self.assertListEqual(select_all_mock.call_args_list, [
            call(cls_mock, name__eq="dummy",
                 order_by="id", order="asc",
                 offset=0, limit=DELETE_ALL_BATCH_SIZE),
            call(cls_mock, name__eq="dummy",
                 order_by="id", order="asc",
                 offset=DELETE_ALL_BATCH_SIZE, limit=DELETE_ALL_BATCH_SIZE),
            call(cls_mock, name__eq="dummy",
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
    async def test_delete_all_commit_false(self, select_all_mock,
                                           delete_mock):
        session_mock = AsyncMock()
        entity_manager = EntityManager(session_mock)

        cls_mock = MagicMock()
        entity_1, entity_2, entity_3 = MagicMock(), MagicMock(), MagicMock()
        select_all_mock.side_effect = [[entity_1, entity_2], [entity_3], []]

        result = await entity_manager.delete_all(
            cls_mock, commit=False, name__eq="dummy")
        self.assertIsNone(result)

        self.assertEqual(select_all_mock.call_count, 3)
        self.assertListEqual(select_all_mock.call_args_list, [
            call(cls_mock, name__eq="dummy",
                 order_by="id", order="asc",
                 offset=0, limit=DELETE_ALL_BATCH_SIZE),
            call(cls_mock, name__eq="dummy",
                 order_by="id", order="asc",
                 offset=DELETE_ALL_BATCH_SIZE, limit=DELETE_ALL_BATCH_SIZE),
            call(cls_mock, name__eq="dummy",
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
    async def test_count_all(self, select_mock, func_mock, where_mock):
        session_mock = AsyncMock()
        entity_manager = EntityManager(session_mock)

        cls_mock = MagicMock()
        result_mock = MagicMock()
        result_mock.unique.return_value.scalars.return_value.one_or_none.return_value = 123 # noqa E501
        session_mock.execute.return_value = result_mock
        kwargs = {"name__eq": "dummy"}

        result = await entity_manager.count_all(
            cls_mock, **kwargs)
        self.assertEqual(result, 123)

        func_mock.count.assert_called_once_with(cls_mock.id)
        where_mock.assert_called_once_with(cls_mock, **kwargs)
        select_mock.assert_called_once_with(func_mock.count.return_value)
        select_mock.return_value.where.assert_called_once_with(
            *where_mock.return_value)
        select_mock.return_value.where.return_value.filter.assert_not_called()
        cls_mock.id.in_.assert_not_called()
        result_mock.unique.return_value.scalars.return_value.one_or_none.assert_called_once() # noqa E501

    @patch("app.managers.entity_manager.EntityManager._where")
    @patch("app.managers.entity_manager.func")
    @patch("app.managers.entity_manager.select")
    async def test_count_all_subquery(self, select_mock, func_mock,
                                      where_mock):
        session_mock = AsyncMock()
        entity_manager = EntityManager(session_mock)

        cls_mock = MagicMock()
        result_mock = MagicMock()
        result_mock.unique.return_value.scalars.return_value.one_or_none.return_value = 123 # noqa E501
        session_mock.execute.return_value = result_mock
        kwargs = {"name__eq": "dummy", "subquery": MagicMock()}

        result = await entity_manager.count_all(
            cls_mock, **kwargs)
        self.assertEqual(result, 123)

        func_mock.count.assert_called_once_with(cls_mock.id)
        where_mock.assert_called_once_with(cls_mock, **kwargs)
        select_mock.assert_called_once_with(func_mock.count.return_value)
        select_mock.return_value.where.assert_called_once_with(
            *where_mock.return_value)
        select_mock.return_value.where.return_value.filter.assert_called_once_with(cls_mock.id.in_.return_value)  # noqa E501
        cls_mock.id.in_.assert_called_once()
        result_mock.unique.return_value.scalars.return_value.one_or_none.assert_called_once() # noqa E501

    @patch("app.managers.entity_manager.EntityManager._where")
    @patch("app.managers.entity_manager.func")
    @patch("app.managers.entity_manager.select")
    async def test_count_all_none(self, select_mock, func_mock, where_mock):
        session_mock = AsyncMock()
        entity_manager = EntityManager(session_mock)

        cls_mock = MagicMock(id=1)
        result_mock = MagicMock()
        result_mock.unique.return_value.scalars.return_value.one_or_none.return_value = None # noqa E501
        session_mock.execute.return_value = result_mock
        kwargs = {"name__eq": "dummy"}

        result = await entity_manager.count_all(cls_mock, **kwargs)
        self.assertEqual(result, 0)

        func_mock.count.assert_called_once_with(cls_mock.id)
        where_mock.assert_called_once_with(cls_mock, **kwargs)
        select_mock.assert_called_once_with(func_mock.count.return_value)
        select_mock.return_value.where.assert_called_once_with(
            *where_mock.return_value)
        result_mock.unique.return_value.scalars.return_value.one_or_none.assert_called_once() # noqa E501

    @patch("app.managers.entity_manager.EntityManager._where")
    @patch("app.managers.entity_manager.func")
    @patch("app.managers.entity_manager.select")
    async def test_sum_all(self, select_mock, func_mock, where_mock):
        session_mock = AsyncMock()
        entity_manager = EntityManager(session_mock)

        cls_mock = MagicMock(name="dummy", number=1)
        result_mock = MagicMock()
        result_mock.unique.return_value.scalars.return_value.one_or_none.return_value = 123 # noqa E501
        session_mock.execute.return_value = result_mock
        kwargs = {"name__eq": "dummy"}

        result = await entity_manager.sum_all(cls_mock, "number", **kwargs)
        self.assertEqual(result, 123)

        func_mock.sum.assert_called_once_with(cls_mock.number)
        where_mock.assert_called_once_with(cls_mock, **kwargs)
        select_mock.assert_called_once_with(func_mock.sum.return_value)
        select_mock.return_value.where.assert_called_once_with(
            *where_mock.return_value)
        select_mock.return_value.where.return_value.filter.assert_not_called()
        cls_mock.id.in_.assert_not_called()
        result_mock.unique.return_value.scalars.return_value.one_or_none.assert_called_once() # noqa E501

    @patch("app.managers.entity_manager.EntityManager._where")
    @patch("app.managers.entity_manager.func")
    @patch("app.managers.entity_manager.select")
    async def test_sum_all_subquery(self, select_mock, func_mock, where_mock):
        session_mock = AsyncMock()
        entity_manager = EntityManager(session_mock)

        cls_mock = MagicMock(name="dummy", number=1)
        result_mock = MagicMock()
        result_mock.unique.return_value.scalars.return_value.one_or_none.return_value = 123 # noqa E501
        session_mock.execute.return_value = result_mock
        kwargs = {"name__eq": "dummy", "subquery": MagicMock()}

        result = await entity_manager.sum_all(cls_mock, "number", **kwargs)
        self.assertEqual(result, 123)

        func_mock.sum.assert_called_once_with(cls_mock.number)
        where_mock.assert_called_once_with(cls_mock, **kwargs)
        select_mock.assert_called_once_with(func_mock.sum.return_value)
        select_mock.return_value.where.assert_called_once_with(
            *where_mock.return_value)
        select_mock.return_value.where.return_value.filter.assert_called_once_with(  # noqa E501
            cls_mock.id.in_.return_value)
        cls_mock.id.in_.assert_called_once()
        result_mock.unique.return_value.scalars.return_value.one_or_none.assert_called_once() # noqa E501

    @patch("app.managers.entity_manager.EntityManager._where")
    @patch("app.managers.entity_manager.func")
    @patch("app.managers.entity_manager.select")
    async def test_sum_all_none(self, select_mock, func_mock, where_mock):
        session_mock = AsyncMock()
        entity_manager = EntityManager(session_mock)

        cls_mock = MagicMock(name="dummy", number=1)
        result_mock = MagicMock()
        result_mock.unique.return_value.scalars.return_value.one_or_none.return_value = None # noqa E501
        session_mock.execute.return_value = result_mock
        kwargs = {"name__eq": "dummy"}

        result = await entity_manager.sum_all(cls_mock, "number", **kwargs)
        self.assertEqual(result, 0)

        func_mock.sum.assert_called_once_with(cls_mock.number)
        where_mock.assert_called_once_with(cls_mock, **kwargs)
        select_mock.assert_called_once_with(func_mock.sum.return_value)
        select_mock.return_value.where.assert_called_once_with(
            *where_mock.return_value)
        result_mock.unique.return_value.scalars.return_value.one_or_none.assert_called_once() # noqa E501

    @patch("app.managers.entity_manager.select")
    async def test_subquery(self, select_mock):
        session_mock = AsyncMock()
        entity_manager = EntityManager(session_mock)

        class_mock = MagicMock(dummy_id="class_column")
        foreign_key = "dummy_id"
        kwargs = {"key__eq": "value"}

        result = await entity_manager.subquery(
            class_mock, foreign_key, **kwargs)
        self.assertTrue(isinstance(result, MagicMock))

        select_mock.assert_called_once_with(class_mock.dummy_id)
        select_mock.return_value.filter.assert_called_once()
        select_mock.return_value.filter.return_value.subquery.assert_called_once()  # noqa E501

    async def test_flush(self):
        session_mock = AsyncMock()
        entity_manager = EntityManager(session_mock)

        result = await entity_manager.flush()
        self.assertIsNone(result)
        session_mock.flush.assert_called_once()

    async def test_commit(self):
        session_mock = AsyncMock()
        entity_manager = EntityManager(session_mock)

        result = await entity_manager.commit()
        self.assertIsNone(result)
        session_mock.commit.assert_called_once()

    async def test_rollback(self):
        session_mock = AsyncMock()
        entity_manager = EntityManager(session_mock)

        result = await entity_manager.rollback()
        self.assertIsNone(result)
        session_mock.rollback.assert_called_once()

    async def test_where(self):
        session_mock = AsyncMock()
        entity_manager = EntityManager(session_mock)

        (in_mock, eq_mock, ne_mock, ge_mock, le_mock, gt_mock, lt_mock,
         like_mock, ilike_mock) = (
            MagicMock(), MagicMock(), MagicMock(), MagicMock(), MagicMock(),
            MagicMock(), MagicMock(), MagicMock(), MagicMock())
        column_mock = MagicMock(
            in_=in_mock, __eq__=eq_mock, __ne__=ne_mock, __ge__=ge_mock,
            __le__=le_mock, __gt__=gt_mock, __lt__=lt_mock, like=like_mock,
            ilike=ilike_mock)
        cls_mock = MagicMock(column=column_mock)
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

        result = entity_manager._where(cls_mock, **kwargs)
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
    async def test_order_by_asc(self, asc_mock):
        session_mock = AsyncMock()
        entity_manager = EntityManager(session_mock)

        column_mock = MagicMock()
        cls_mock = MagicMock(column=column_mock)
        kwargs = {"order_by": "column", "order": "asc"}
        result = entity_manager._order_by(cls_mock, **kwargs)

        self.assertEqual(result, asc_mock.return_value)
        asc_mock.assert_called_once_with(column_mock)

    @patch("app.managers.entity_manager.desc")
    async def test_order_by_desc(self, desc_mock):
        session_mock = AsyncMock()
        entity_manager = EntityManager(session_mock)

        column_mock = MagicMock()
        cls_mock = MagicMock(column=column_mock)
        kwargs = {"order_by": "column", "order": "desc"}

        result = entity_manager._order_by(cls_mock, **kwargs)
        self.assertEqual(result, desc_mock.return_value)

        desc_mock.assert_called_once_with(column_mock)

    @patch("app.managers.entity_manager.func")
    async def test_order_by_rand(self, func_mock):
        session_mock = AsyncMock()
        entity_manager = EntityManager(session_mock)

        column_mock = MagicMock()
        cls_mock = MagicMock(column=column_mock)
        kwargs = {"order_by": "column", "order": "rand"}

        result = entity_manager._order_by(cls_mock, **kwargs)
        self.assertEqual(result, func_mock.random.return_value)

    async def test_offset(self):
        session_mock = AsyncMock()
        entity_manager = EntityManager(session_mock)

        kwargs = {"offset": 123}
        result = entity_manager._offset(**kwargs)
        self.assertEqual(result, 123)

    async def test_limit(self):
        session_mock = AsyncMock()
        entity_manager = EntityManager(session_mock)

        kwargs = {"limit": 123}
        result = entity_manager._limit(**kwargs)
        self.assertEqual(result, 123)


if __name__ == "__main__":
    unittest.main()
