import unittest
from unittest.mock import AsyncMock, MagicMock, patch
from app.routers.user_password_router import user_password
from app.hook import HOOK_AFTER_USER_PASSWORD
from app.error import E


class UserPasswordRouterTest(unittest.IsolatedAsyncioTestCase):

    @patch("app.routers.user_password_router.hash_str")
    @patch("app.routers.user_password_router.Hook")
    @patch("app.routers.user_password_router.Repository")
    async def test_user_password_success(self, RepositoryMock, HookMock,
                                         hash_str_mock):
        request_mock = MagicMock()
        schema_mock = AsyncMock(current_password="current",
                                updated_password="updated")
        session_mock = AsyncMock()
        cache_mock = AsyncMock()
        current_user_mock = AsyncMock(id=123, password_hash="current-hashed")

        repository_mock = AsyncMock()
        RepositoryMock.return_value = repository_mock

        hook_mock = AsyncMock()
        HookMock.return_value = hook_mock

        hash_str_mock.side_effect = ["current-hashed", "updated-hashed"]

        result = await user_password(
            123, schema_mock, request_mock, session=session_mock,
            cache=cache_mock, current_user=current_user_mock)

        self.assertEqual(result, {"user_id": 123})

        self.assertEqual(current_user_mock.password_hash, "updated-hashed")
        repository_mock.update.assert_called_with(current_user_mock)

        HookMock.assert_called_with(
            request_mock.app, session_mock, cache_mock,
            current_user=current_user_mock)
        hook_mock.call.assert_called_with(HOOK_AFTER_USER_PASSWORD,
                                          current_user_mock)

    @patch("app.routers.user_password_router.Hook")
    @patch("app.routers.user_password_router.Repository")
    async def test_user_password_user_not_found(self, RepositoryMock,
                                                HookMock):
        request_mock = MagicMock()
        schema_mock = AsyncMock(current_password="current",
                                updated_password="updated")
        session_mock = AsyncMock()
        cache_mock = AsyncMock()
        current_user_mock = AsyncMock(id=123, password_hash="current-hashed")

        repository_mock = AsyncMock()
        RepositoryMock.return_value = repository_mock

        hook_mock = AsyncMock()
        HookMock.return_value = hook_mock

        with self.assertRaises(E) as context:
            await user_password(
                234, schema_mock, request_mock, session=session_mock,
                cache=cache_mock, current_user=current_user_mock)

        repository_mock.update.assert_not_called()

        self.assertEqual(context.exception.status_code, 422)
        self.assertEqual(context.exception.detail[0]["type"], "value_error")
        self.assertTrue("user_id" in context.exception.detail[0]["loc"])

        HookMock.assert_not_called()
        hook_mock.call.assert_not_called()

    @patch("app.routers.user_password_router.hash_str")
    @patch("app.routers.user_password_router.Hook")
    @patch("app.routers.user_password_router.Repository")
    async def test_user_password_password_invalid(self, RepositoryMock,
                                                  HookMock, hash_str_mock):
        request_mock = MagicMock()
        schema_mock = AsyncMock(current_password="current",
                                updated_password="updated")
        session_mock = AsyncMock()
        cache_mock = AsyncMock()
        current_user_mock = AsyncMock(id=123, password_hash="invalid-hashed")

        repository_mock = AsyncMock()
        RepositoryMock.return_value = repository_mock

        hash_str_mock.return_value = "current-hashed"

        hook_mock = AsyncMock()
        HookMock.return_value = hook_mock

        with self.assertRaises(E) as context:
            await user_password(
                123, schema_mock, request_mock, session=session_mock,
                cache=cache_mock, current_user=current_user_mock)

        repository_mock.update.assert_not_called()

        self.assertEqual(context.exception.status_code, 422)
        self.assertEqual(context.exception.detail[0]["type"], "value_error")
        self.assertTrue("current_password" in context.exception.detail[0]["loc"])  # noqa E501

        HookMock.assert_not_called()
        hook_mock.call.assert_not_called()

    @patch("app.routers.user_password_router.hash_str")
    @patch("app.routers.user_password_router.Hook")
    @patch("app.routers.user_password_router.Repository")
    async def test_user_password_passwords_equal(self, RepositoryMock,
                                                 HookMock, hash_str_mock):
        request_mock = MagicMock()
        schema_mock = AsyncMock(current_password="current",
                                updated_password="current")
        session_mock = AsyncMock()
        cache_mock = AsyncMock()
        current_user_mock = AsyncMock(id=123, password_hash="current-hashed")

        repository_mock = AsyncMock()
        RepositoryMock.return_value = repository_mock

        hash_str_mock.side_effect = ["current-hashed", "current-hashed"]

        hook_mock = AsyncMock()
        HookMock.return_value = hook_mock

        with self.assertRaises(E) as context:
            await user_password(
                123, schema_mock, request_mock, session=session_mock,
                cache=cache_mock, current_user=current_user_mock)

        repository_mock.update.assert_not_called()

        self.assertEqual(context.exception.status_code, 422)
        self.assertEqual(context.exception.detail[0]["type"], "value_error")
        self.assertTrue("updated_password" in context.exception.detail[0]["loc"])  # noqa E501

        HookMock.assert_not_called()
        hook_mock.call.assert_not_called()


if __name__ == "__main__":
    unittest.main()
