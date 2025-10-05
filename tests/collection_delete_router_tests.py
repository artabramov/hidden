import unittest
from unittest.mock import AsyncMock, MagicMock, patch, call
from app.routers.collection_delete import (
    collection_delete, Collection, Document)
from app.hook import HOOK_AFTER_COLLECTION_DELETE
from app.error import E
from app.config import get_config


class CollectionDeleteRouterTest(unittest.IsolatedAsyncioTestCase):

    @patch("app.routers.collection_delete.Hook")
    @patch("app.routers.collection_delete.Repository")
    async def test_collection_delete_success(self, RepositoryMock, HookMock):

        request = MagicMock()
        request.app = MagicMock()
        request.app.state = MagicMock()
        request.app.state.config = get_config()

        lru_mock = MagicMock()
        request.app.state.lru = lru_mock

        file_manager_mock = AsyncMock()
        request.app.state.file_manager = file_manager_mock

        collection_locks_mock = AsyncMock()
        request.app.state.collection_locks = collection_locks_mock

        session = AsyncMock()
        cache = AsyncMock()
        current_user = AsyncMock()

        collection_repository = AsyncMock()
        collection_mock = AsyncMock(
            id=42, path=MagicMock(return_value="collection-path"))
        collection_repository.select.return_value = collection_mock

        document_37 = AsyncMock(
            id=37,
            has_thumbnail=True,
            document_thumbnail=MagicMock(
                path=MagicMock(return_value="thumb37")),
            path=MagicMock(return_value="path37"),
            has_revisions=True,
            document_revisions=[
                MagicMock(path=MagicMock(return_value="rev37-1")),
                MagicMock(path=MagicMock(return_value="rev37-1"))
            ]
        )

        document_38 = AsyncMock(
            id=38,
            has_thumbnail=True,
            document_thumbnail=MagicMock(
                path=MagicMock(return_value="thumb38")),
            path=MagicMock(return_value="path38"),
            has_revisions=True,
            document_revisions=[
                MagicMock(path=MagicMock(return_value="rev38-1")),
                MagicMock(path=MagicMock(return_value="rev38-1"))
            ]
        )

        document_repository = AsyncMock()
        document_repository.select_all.return_value = [
            document_37, document_38]

        RepositoryMock.side_effect = [
            collection_repository,
            document_repository
        ]

        hook = AsyncMock()
        HookMock.return_value = hook

        result = await collection_delete(
            request, 42,
            session=session, cache=cache,
            current_user=current_user
        )

        self.assertEqual(result, {"collection_id": collection_mock.id})

        self.assertListEqual(RepositoryMock.call_args_list, [
            call(session, cache, Collection, request.app.state.config),
            call(session, cache, Document, request.app.state.config),
        ])

        collection_repository.select.assert_awaited_with(id=42)
        document_repository.select_all.assert_awaited_with(
            collection_id__eq=42)

        collection_locks_mock.__getitem__.assert_called_once_with(42)

        file_manager_mock.delete.assert_has_awaits([
            call("thumb37"), call("rev37-1"), call("rev37-1"), call("path37"),
            call("thumb38"), call("rev38-1"), call("rev38-1"), call("path38"),
        ], any_order=True)

        lru_mock.delete.assert_has_calls([
            call("thumb37"), call("rev37-1"), call("rev37-1"), call("path37"),
            call("thumb38"), call("rev38-1"), call("rev38-1"), call("path38"),
        ], any_order=True)

        document_repository.delete.assert_has_awaits([
            call(document_37), call(document_38)
        ], any_order=True)

        collection_repository.delete.assert_awaited_with(collection_mock)

        file_manager_mock.rmdir.assert_awaited_with("collection-path")

        HookMock.assert_called_with(
            request, session, cache, current_user=current_user)
        hook.call.assert_awaited_with(HOOK_AFTER_COLLECTION_DELETE, 42)

    @patch("app.routers.collection_delete.Hook")
    @patch("app.routers.collection_delete.Repository")
    async def test_collection_delete_not_found(self, RepositoryMock, HookMock):

        request = MagicMock()
        request.app = MagicMock()
        request.app.state = MagicMock()
        request.app.state.config = get_config()

        session = AsyncMock()
        cache = AsyncMock()
        current_user = AsyncMock()

        collection_repository = AsyncMock()
        collection_repository.select.return_value = None

        RepositoryMock.side_effect = [
            collection_repository
        ]

        hook = AsyncMock()
        HookMock.return_value = hook

        with self.assertRaises(E) as ctx:
            await collection_delete(
                request, 42,
                session=session, cache=cache,
                current_user=current_user
            )

        collection_repository.select.assert_awaited_with(id=42)

        self.assertEqual(ctx.exception.status_code, 404)
        self.assertEqual(ctx.exception.detail[0]["type"], "value_not_found")
        self.assertIn("collection_id", ctx.exception.detail[0]["loc"])

        HookMock.assert_not_called()
        hook.call.assert_not_called()
