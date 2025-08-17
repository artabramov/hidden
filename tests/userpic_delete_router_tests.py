import unittest
from unittest.mock import AsyncMock, MagicMock, patch
from app.routers.userpic_delete_router import userpic_delete
from app.hook import HOOK_AFTER_USERPIC_DELETE
from app.error import E
from app.config import get_config

cfg = get_config()


class UserpicDeleteRouterTest(unittest.IsolatedAsyncioTestCase):

    @patch("app.routers.userpic_delete_router.Hook")
    async def test_userpic_delete_user_invalid(self, HookMock):
        request_mock = MagicMock()
        session_mock = AsyncMock()
        cache_mock = AsyncMock()
        current_user_mock = AsyncMock(id=123)

        hook_mock = AsyncMock()
        HookMock.return_value = hook_mock

        with self.assertRaises(E) as context:
            await userpic_delete(
                234, request_mock, session=session_mock, cache=cache_mock,
                current_user=current_user_mock)

        self.assertEqual(context.exception.status_code, 422)
        self.assertEqual(context.exception.detail[0]["type"], "value_error")
        self.assertTrue("user_id" in context.exception.detail[0]["loc"])

        HookMock.assert_not_called()
        hook_mock.call.assert_not_called()

    @patch("app.routers.userpic_delete_router.FileManager",
           new_callable=AsyncMock)
    @patch("app.routers.userpic_delete_router.Repository")
    @patch("app.routers.userpic_delete_router.Hook")
    async def test_userpic_delete_none(self, HookMock, RepositoryMock,
                                       FileManagerMock):
        request_mock = MagicMock()
        session_mock = AsyncMock()
        cache_mock = AsyncMock()
        current_user_mock = AsyncMock(id=123, has_userpic=False,
                                      userpic_filename=None)

        repository_mock = AsyncMock()
        RepositoryMock.return_value = repository_mock

        hook_mock = AsyncMock()
        HookMock.return_value = hook_mock

        result = await userpic_delete(
            123, request_mock, session=session_mock, cache=cache_mock,
            current_user=current_user_mock)
        self.assertDictEqual(result, {"user_id": 123})

        FileManagerMock.delete.assert_not_called()
        self.assertIsNone(current_user_mock.userpic_filename)
        repository_mock.update.assert_not_called()

        HookMock.assert_called_with(
            request_mock.app, session_mock, cache_mock,
            current_user=current_user_mock)
        hook_mock.call.assert_called_with(HOOK_AFTER_USERPIC_DELETE,
                                          current_user_mock)

    @patch("app.routers.userpic_delete_router.FileManager",
           new_callable=AsyncMock)
    @patch("app.routers.userpic_delete_router.Repository")
    @patch("app.routers.userpic_delete_router.Hook")
    async def test_userpic_delete_success(self, HookMock, RepositoryMock,
                                          FileManagerMock):
        request_mock = MagicMock()
        session_mock = AsyncMock()
        cache_mock = AsyncMock()
        current_user_mock = AsyncMock(id=123, has_userpic=True,
                                      userpic_filename="filename")

        repository_mock = AsyncMock()
        RepositoryMock.return_value = repository_mock

        hook_mock = AsyncMock()
        HookMock.return_value = hook_mock

        result = await userpic_delete(
            123, request_mock, session=session_mock, cache=cache_mock,
            current_user=current_user_mock)
        self.assertDictEqual(result, {"user_id": 123})

        FileManagerMock.delete.assert_called_with(
            current_user_mock.userpic_path)
        self.assertIsNone(current_user_mock.userpic_filename)
        repository_mock.update.assert_called_with(current_user_mock)

        HookMock.assert_called_with(
            request_mock.app, session_mock, cache_mock,
            current_user=current_user_mock)
        hook_mock.call.assert_called_with(HOOK_AFTER_USERPIC_DELETE,
                                          current_user_mock)


if __name__ == "__main__":
    unittest.main()
