import unittest
from unittest.mock import AsyncMock, MagicMock, patch
from app.routers.user_select_router import user_select
from app.hook import HOOK_AFTER_USER_SELECT
from app.error import E


class UserSelectRouterTest(unittest.IsolatedAsyncioTestCase):

    @patch("app.routers.user_select_router.Hook")
    @patch("app.routers.user_select_router.Repository")
    async def test_user_select_success(self, RepositoryMock, HookMock):
        request_mock = MagicMock()
        session_mock = AsyncMock()
        cache_mock = AsyncMock()
        current_user_mock = AsyncMock()

        user_mock = AsyncMock(id=123)
        user_mock.to_dict.return_value = {"id": 123, "username": "johndoe"}

        repository_mock = AsyncMock()
        repository_mock.select.return_value = user_mock
        RepositoryMock.return_value = repository_mock

        hook_mock = AsyncMock()
        HookMock.return_value = hook_mock

        result = await user_select(
            123, request_mock, session=session_mock, cache=cache_mock,
            current_user=current_user_mock)

        self.assertEqual(result, user_mock.to_dict.return_value)
        repository_mock.select.assert_called_with(id=123)

        HookMock.assert_called_with(
            request_mock.app, session_mock, cache_mock,
            current_user=current_user_mock)
        hook_mock.call.assert_called_with(HOOK_AFTER_USER_SELECT, user_mock)

    @patch("app.routers.user_select_router.Hook")
    @patch("app.routers.user_select_router.Repository")
    async def test_user_select_not_found(self, RepositoryMock, HookMock):
        request_mock = MagicMock()
        repository_mock = AsyncMock()
        repository_mock.select.return_value = None
        RepositoryMock.return_value = repository_mock

        hook_mock = AsyncMock()
        HookMock.return_value = hook_mock

        with self.assertRaises(E) as context:
            await user_select(123, request_mock)

        repository_mock.select.assert_called_with(id=123)

        self.assertEqual(context.exception.status_code, 404)
        self.assertEqual(context.exception.detail[0]["type"], "value_not_found")  # noqa E501
        self.assertTrue("user_id" in context.exception.detail[0]["loc"])

        HookMock.assert_not_called()
        hook_mock.call.assert_not_called()


if __name__ == "__main__":
    unittest.main()
