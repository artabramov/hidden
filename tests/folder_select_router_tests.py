import unittest
from unittest.mock import AsyncMock, MagicMock, patch
from app.routers.folder_select import folder_select
from app.hook import HOOK_AFTER_FOLDER_SELECT
from app.error import E
from app.config import get_config


class FolderSelectRouterTest(unittest.IsolatedAsyncioTestCase):

    @patch("app.routers.folder_select.Hook")
    @patch("app.routers.folder_select.Repository")
    async def test_folder_select_success(self, RepositoryMock, HookMock):

        request = MagicMock()
        request.app = MagicMock()
        request.app.state = MagicMock()
        request.app.state.config = get_config()

        session = AsyncMock()
        cache = AsyncMock()
        current_user = AsyncMock()

        folder = AsyncMock(id=123)
        folder.to_dict = AsyncMock(
            return_value={"id": 123, "name": "dummy"})

        folder_repository = AsyncMock()
        folder_repository.select.return_value = folder
        RepositoryMock.return_value = folder_repository

        hook = AsyncMock()
        HookMock.return_value = hook

        result = await folder_select(
            request, 123, session=session, cache=cache,
            current_user=current_user
        )

        self.assertEqual(result, await folder.to_dict())
        folder_repository.select.assert_awaited_with(id=123)

        HookMock.assert_called_with(
            request, session, cache, current_user=current_user)
        hook.call.assert_awaited_with(HOOK_AFTER_FOLDER_SELECT, folder)

    @patch("app.routers.folder_select.Hook")
    @patch("app.routers.folder_select.Repository")
    async def test_folder_select_not_found(self, RepositoryMock, HookMock):

        request = MagicMock()
        request.app = MagicMock()
        request.app.state = MagicMock()
        request.app.state.config = get_config()

        session = AsyncMock()
        cache = AsyncMock()
        current_user = AsyncMock()

        folder_repository = AsyncMock()
        folder_repository.select.return_value = None
        RepositoryMock.return_value = folder_repository

        hook = AsyncMock()
        HookMock.return_value = hook

        with self.assertRaises(E) as ctx:
            await folder_select(
                request, 123, session=session, cache=cache,
                current_user=current_user)

        folder_repository.select.assert_awaited_with(id=123)

        self.assertEqual(ctx.exception.status_code, 404)
        self.assertEqual(ctx.exception.detail[0]["type"], "value_not_found")
        self.assertIn("folder_id", ctx.exception.detail[0]["loc"])

        HookMock.assert_not_called()
        hook.call.assert_not_called()
