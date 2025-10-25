import unittest
from unittest.mock import AsyncMock, MagicMock, patch
from app.routers.file_select import file_select
from app.hook import HOOK_AFTER_FILE_SELECT
from app.error import E
from app.config import get_config


class FileSelectRouterTest(unittest.IsolatedAsyncioTestCase):

    @patch("app.routers.file_select.Hook")
    @patch("app.routers.file_select.Repository")
    async def test_file_select_success(self, RepositoryMock, HookMock):

        request = MagicMock()
        request.app = MagicMock()
        request.app.state = MagicMock()
        request.app.state.config = get_config()

        session = AsyncMock()
        cache = AsyncMock()
        current_user = AsyncMock()

        file = AsyncMock(id=37)
        file.to_dict = AsyncMock(
            return_value={"id": file.id, "name": "doc"})

        file_repository = AsyncMock()
        file_repository.select.return_value = file

        RepositoryMock.return_value = file_repository

        hook = AsyncMock()
        HookMock.return_value = hook

        result = await file_select(
            request, file.id,
            session=session, cache=cache,
            current_user=current_user
        )

        self.assertEqual(result, await file.to_dict())
        file_repository.select.assert_awaited_with(id=file.id)

        HookMock.assert_called_with(
            request, session, cache, current_user=current_user)
        hook.call.assert_awaited_with(HOOK_AFTER_FILE_SELECT, file)

    @patch("app.routers.file_select.Hook")
    @patch("app.routers.file_select.Repository")
    async def test_file_select_file_not_found(
            self, RepositoryMock, HookMock):

        request = MagicMock()
        request.app = MagicMock()
        request.app.state = MagicMock()
        request.app.state.config = get_config()

        session = AsyncMock()
        cache = AsyncMock()
        current_user = AsyncMock()

        file_repository = AsyncMock()
        file_repository.select.return_value = None

        RepositoryMock.return_value = file_repository

        hook = AsyncMock()
        HookMock.return_value = hook

        with self.assertRaises(E) as ctx:
            await file_select(
                request, 37,
                session=session, cache=cache,
                current_user=current_user
            )

        file_repository.select.assert_awaited_with(id=37)

        self.assertEqual(ctx.exception.status_code, 404)
        self.assertEqual(ctx.exception.detail[0]["type"], "value_not_found")
        self.assertIn("file_id", ctx.exception.detail[0]["loc"])

        HookMock.assert_not_called()
        hook.call.assert_not_called()
