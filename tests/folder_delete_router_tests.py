import unittest
from unittest.mock import AsyncMock, MagicMock, patch, call
from app.routers.folder_delete import folder_delete, Folder, File
from app.hook import HOOK_AFTER_FOLDER_DELETE
from app.error import E
from app.config import get_config


class FolderDeleteRouterTest(unittest.IsolatedAsyncioTestCase):

    @patch("app.routers.folder_delete.Hook")
    @patch("app.routers.folder_delete.Repository")
    async def test_folder_delete_success(self, RepositoryMock, HookMock):

        request = MagicMock()
        request.app = MagicMock()
        request.app.state = MagicMock()
        request.app.state.config = get_config()

        lru_mock = MagicMock()
        request.app.state.lru = lru_mock

        file_manager_mock = AsyncMock()
        request.app.state.file_manager = file_manager_mock

        folder_locks_mock = AsyncMock()
        request.app.state.folder_locks = folder_locks_mock

        session = AsyncMock()
        cache = AsyncMock()
        current_user = AsyncMock()

        folder_repository = AsyncMock()
        folder_mock = AsyncMock(
            id=42, path=MagicMock(return_value="folder-path"))
        folder_repository.select.return_value = folder_mock

        file_37 = AsyncMock(
            id=37,
            has_thumbnail=True,
            file_thumbnail=MagicMock(
                path=MagicMock(return_value="thumb37")),
            path=MagicMock(return_value="path37"),
            has_revisions=True,
            file_revisions=[
                MagicMock(path=MagicMock(return_value="rev37-1")),
                MagicMock(path=MagicMock(return_value="rev37-1"))
            ]
        )

        file_38 = AsyncMock(
            id=38,
            has_thumbnail=True,
            file_thumbnail=MagicMock(
                path=MagicMock(return_value="thumb38")),
            path=MagicMock(return_value="path38"),
            has_revisions=True,
            file_revisions=[
                MagicMock(path=MagicMock(return_value="rev38-1")),
                MagicMock(path=MagicMock(return_value="rev38-1"))
            ]
        )

        file_repository = AsyncMock()
        file_repository.select_all.return_value = [
            file_37, file_38]

        RepositoryMock.side_effect = [
            folder_repository,
            file_repository
        ]

        hook = AsyncMock()
        HookMock.return_value = hook

        result = await folder_delete(
            request, 42,
            session=session, cache=cache,
            current_user=current_user
        )

        self.assertEqual(result, {"folder_id": folder_mock.id})

        self.assertListEqual(RepositoryMock.call_args_list, [
            call(session, cache, Folder, request.app.state.config),
            call(session, cache, File, request.app.state.config),
        ])

        folder_repository.select.assert_awaited_with(id=42)
        file_repository.select_all.assert_awaited_with(
            folder_id__eq=42)

        folder_locks_mock.__getitem__.assert_called_once_with(42)

        file_manager_mock.delete.assert_has_awaits([
            call("thumb37"), call("rev37-1"), call("rev37-1"), call("path37"),
            call("thumb38"), call("rev38-1"), call("rev38-1"), call("path38"),
        ], any_order=True)

        lru_mock.delete.assert_has_calls([
            call("thumb37"), call("rev37-1"), call("rev37-1"), call("path37"),
            call("thumb38"), call("rev38-1"), call("rev38-1"), call("path38"),
        ], any_order=True)

        file_repository.delete.assert_has_awaits([
            call(file_37), call(file_38)
        ], any_order=True)

        folder_repository.delete.assert_awaited_with(folder_mock)

        file_manager_mock.rmdir.assert_awaited_with("folder-path")

        HookMock.assert_called_with(
            request, session, cache, current_user=current_user)
        hook.call.assert_awaited_with(HOOK_AFTER_FOLDER_DELETE, 42)

    @patch("app.routers.folder_delete.Hook")
    @patch("app.routers.folder_delete.Repository")
    async def test_folder_delete_not_found(self, RepositoryMock, HookMock):

        request = MagicMock()
        request.app = MagicMock()
        request.app.state = MagicMock()
        request.app.state.config = get_config()

        session = AsyncMock()
        cache = AsyncMock()
        current_user = AsyncMock()

        folder_repository = AsyncMock()
        folder_repository.select.return_value = None

        RepositoryMock.side_effect = [
            folder_repository
        ]

        hook = AsyncMock()
        HookMock.return_value = hook

        with self.assertRaises(E) as ctx:
            await folder_delete(
                request, 42,
                session=session, cache=cache,
                current_user=current_user
            )

        folder_repository.select.assert_awaited_with(id=42)

        self.assertEqual(ctx.exception.status_code, 404)
        self.assertEqual(ctx.exception.detail[0]["type"], "value_not_found")
        self.assertIn("folder_id", ctx.exception.detail[0]["loc"])

        HookMock.assert_not_called()
        hook.call.assert_not_called()
