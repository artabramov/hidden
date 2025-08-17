import unittest
from unittest.mock import AsyncMock, MagicMock, patch
from app.routers.user_update_router import user_update
from app.hook import HOOK_AFTER_USER_UPDATE
from app.error import E


class UserUpdateRouterTest(unittest.IsolatedAsyncioTestCase):

    @patch("app.routers.user_update_router.Hook")
    @patch("app.routers.user_update_router.Repository")
    async def test_user_update_success(self, RepositoryMock, HookMock):
        schema_mock = AsyncMock(first_name="John", last_name="Doe",
                                user_summary="lorem ipsum")
        request_mock = MagicMock()
        session_mock = AsyncMock()
        cache_mock = AsyncMock()
        current_user_mock = AsyncMock(id=123)

        repository_mock = AsyncMock()
        RepositoryMock.return_value = repository_mock

        hook_mock = AsyncMock()
        HookMock.return_value = hook_mock

        result = await user_update(
            123, schema_mock, request_mock, session=session_mock,
            cache=cache_mock, current_user=current_user_mock)

        self.assertEqual(result, {"user_id": 123})

        self.assertEqual(current_user_mock.first_name, "John")
        self.assertEqual(current_user_mock.last_name, "Doe")
        self.assertEqual(current_user_mock.user_summary, "lorem ipsum")
        repository_mock.update.assert_called_with(current_user_mock)

        HookMock.assert_called_with(
            request_mock.app, session_mock, cache_mock,
            current_user=current_user_mock)
        hook_mock.call.assert_called_with(HOOK_AFTER_USER_UPDATE,
                                          current_user_mock)

    @patch("app.routers.user_update_router.Hook")
    async def test_user_update_error(self, HookMock):
        request_mock = MagicMock()
        schema_mock = AsyncMock()
        session_mock = AsyncMock()
        cache_mock = AsyncMock()
        current_user_mock = AsyncMock(id=123)

        hook_mock = AsyncMock()
        HookMock.return_value = hook_mock

        with self.assertRaises(E) as context:
            await user_update(
                234, schema_mock, request_mock, session=session_mock,
                cache=cache_mock, current_user=current_user_mock)

        self.assertEqual(context.exception.status_code, 422)
        self.assertEqual(context.exception.detail[0]["type"], "value_error")
        self.assertTrue("user_id" in context.exception.detail[0]["loc"])

        HookMock.assert_not_called()
        hook_mock.call.assert_not_called()


if __name__ == "__main__":
    unittest.main()
