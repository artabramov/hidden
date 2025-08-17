import unittest
from unittest.mock import AsyncMock, MagicMock, patch
from app.routers.user_role_router import user_role
from app.hook import HOOK_AFTER_USER_ROLE
from app.error import E


class UserRoleRouterTest(unittest.IsolatedAsyncioTestCase):

    @patch("app.routers.user_role_router.Hook")
    @patch("app.routers.user_role_router.Repository")
    async def test_user_role_user_invalid(self, RepositoryMock, HookMock):
        request_mock = MagicMock()
        schema_mock = AsyncMock(user_role="reader", is_active=True)
        session_mock = AsyncMock()
        cache_mock = AsyncMock()
        current_user_mock = AsyncMock(id=123)

        repository_mock = AsyncMock()
        repository_mock.select.return_value = None
        RepositoryMock.return_value = repository_mock

        hook_mock = AsyncMock()
        HookMock.return_value = hook_mock

        with self.assertRaises(E) as context:
            await user_role(
                234, schema_mock, request_mock, session=session_mock,
                cache=cache_mock, current_user=current_user_mock)

        repository_mock.update.assert_not_called()

        self.assertEqual(context.exception.status_code, 404)
        self.assertEqual(context.exception.detail[0]["type"], "value_not_found")  # noqa E501
        self.assertTrue("user_id" in context.exception.detail[0]["loc"])

        HookMock.assert_not_called()
        hook_mock.call.assert_not_called()

    @patch("app.routers.user_role_router.Hook")
    @patch("app.routers.user_role_router.Repository")
    async def test_user_role_current_user(self, RepositoryMock, HookMock):
        request_mock = MagicMock()
        schema_mock = AsyncMock(user_role="reader", is_active=True)
        session_mock = AsyncMock()
        cache_mock = AsyncMock()
        current_user_mock = AsyncMock(id=123)

        user_mock = AsyncMock(id=123)

        repository_mock = AsyncMock()
        repository_mock.select.return_value = user_mock
        RepositoryMock.return_value = repository_mock

        hook_mock = AsyncMock()
        HookMock.return_value = hook_mock

        with self.assertRaises(E) as context:
            await user_role(
                123, schema_mock, request_mock, session=session_mock,
                cache=cache_mock, current_user=current_user_mock)

        repository_mock.update.assert_not_called()

        self.assertEqual(context.exception.status_code, 422)
        self.assertEqual(context.exception.detail[0]["type"], "value_error")
        self.assertTrue("user_id" in context.exception.detail[0]["loc"])

        HookMock.assert_not_called()
        hook_mock.call.assert_not_called()

    @patch("app.routers.user_role_router.Hook")
    @patch("app.routers.user_role_router.Repository")
    async def test_user_role_success(self, RepositoryMock, HookMock):
        request_mock = MagicMock()
        schema_mock = AsyncMock(user_role="reader", is_active=True)
        session_mock = AsyncMock()
        cache_mock = AsyncMock()
        current_user_mock = AsyncMock(id=123)

        user_mock = AsyncMock(id=234)

        repository_mock = AsyncMock()
        repository_mock.select.return_value = user_mock
        RepositoryMock.return_value = repository_mock

        hook_mock = AsyncMock()
        HookMock.return_value = hook_mock

        result = await user_role(
                234, schema_mock, request_mock, session=session_mock,
                cache=cache_mock, current_user=current_user_mock)

        self.assertEqual(result, {"user_id": user_mock.id})

        self.assertTrue(user_mock.is_active)
        self.assertEqual(user_mock.user_role, "reader")
        repository_mock.update.assert_called_with(user_mock)

        HookMock.assert_called_with(
            request_mock.app, session_mock, cache_mock,
            current_user=current_user_mock)
        hook_mock.call.assert_called_with(HOOK_AFTER_USER_ROLE, user_mock)


if __name__ == "__main__":
    unittest.main()
