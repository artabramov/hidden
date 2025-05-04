import unittest
import time
from unittest.mock import AsyncMock, patch
from app.routers.user_login_router import user_login
from app.hook import HOOK_AFTER_USER_LOGIN
from app.config import get_config
from app.error import E

cfg = get_config()


class UserLoginRouterTest(unittest.IsolatedAsyncioTestCase):

    @patch("app.routers.user_login_router.hash_str")
    @patch("app.routers.user_login_router.Repository")
    @patch("app.routers.user_login_router.Hook")
    async def test_login_user_not_found(self, HookMock, RepositoryMock,
                                        hash_str_mock):
        schema_mock = AsyncMock(username="username")
        session_mock = AsyncMock()
        cache_mock = AsyncMock()

        hook_mock = AsyncMock()
        HookMock.return_value = hook_mock

        repository_mock = AsyncMock()
        repository_mock.select.return_value = None
        RepositoryMock.return_value = repository_mock

        with self.assertRaises(E) as context:
            await user_login(
                schema=schema_mock, session=session_mock, cache=cache_mock)

        self.assertEqual(context.exception.status_code, 422)
        self.assertEqual(context.exception.detail[0]["type"], "value_error")
        self.assertTrue("username" in context.exception.detail[0]["loc"])

        HookMock.assert_not_called()
        hook_mock.call.assert_not_called()

    @patch("app.routers.user_login_router.hash_str")
    @patch("app.routers.user_login_router.Repository")
    @patch("app.routers.user_login_router.Hook")
    async def test_login_user_suspended(self, HookMock, RepositoryMock,
                                        hash_str_mock):
        schema_mock = AsyncMock(username="username")
        session_mock = AsyncMock()
        cache_mock = AsyncMock()

        hook_mock = AsyncMock()
        HookMock.return_value = hook_mock

        suspended_date = int(time.time()) + 60
        user_mock = AsyncMock(id=123, suspended_date=suspended_date)

        repository_mock = AsyncMock()
        repository_mock.select.return_value = user_mock
        RepositoryMock.return_value = repository_mock

        with self.assertRaises(E) as context:
            await user_login(
                schema=schema_mock, session=session_mock, cache=cache_mock)

        self.assertEqual(context.exception.status_code, 422)
        self.assertEqual(context.exception.detail[0]["type"], "user_suspended")
        self.assertTrue("username" in context.exception.detail[0]["loc"])

        HookMock.assert_not_called()
        hook_mock.call.assert_not_called()

    @patch("app.routers.user_login_router.hash_str")
    @patch("app.routers.user_login_router.Repository")
    @patch("app.routers.user_login_router.Hook")
    async def test_login_user_inactive(self, HookMock, RepositoryMock,
                                       hash_str_mock):
        schema_mock = AsyncMock(username="username")
        session_mock = AsyncMock()
        cache_mock = AsyncMock()

        hook_mock = AsyncMock()
        HookMock.return_value = hook_mock

        user_mock = AsyncMock(id=123, suspended_date=0, is_active=False)

        repository_mock = AsyncMock()
        repository_mock.select.return_value = user_mock
        RepositoryMock.return_value = repository_mock

        with self.assertRaises(E) as context:
            await user_login(
                schema=schema_mock, session=session_mock, cache=cache_mock)

        self.assertEqual(context.exception.status_code, 422)
        self.assertEqual(context.exception.detail[0]["type"], "user_inactive")
        self.assertTrue("username" in context.exception.detail[0]["loc"])

        HookMock.assert_not_called()
        hook_mock.call.assert_not_called()

    @patch("app.routers.user_login_router.hash_str")
    @patch("app.routers.user_login_router.Repository")
    @patch("app.routers.user_login_router.Hook")
    async def test_login_password_invalid(self, HookMock, RepositoryMock,
                                          hash_str_mock):
        schema_mock = AsyncMock(username="username", password="password")
        session_mock = AsyncMock()
        cache_mock = AsyncMock()

        hook_mock = AsyncMock()
        HookMock.return_value = hook_mock

        user_mock = AsyncMock(id=123, suspended_date=0, is_active=True,
                              password_hash="hash", password_attempts=1)

        repository_mock = AsyncMock()
        repository_mock.select.return_value = user_mock
        RepositoryMock.return_value = repository_mock

        with self.assertRaises(E) as context:
            await user_login(
                schema=schema_mock, session=session_mock, cache=cache_mock)

        self.assertEqual(user_mock.password_attempts, 2)
        self.assertEqual(user_mock.suspended_date, 0)
        repository_mock.update.assert_called_with(user_mock)

        self.assertEqual(context.exception.status_code, 422)
        self.assertEqual(context.exception.detail[0]["type"], "value_error")
        self.assertTrue("password" in context.exception.detail[0]["loc"])

        HookMock.assert_not_called()
        hook_mock.call.assert_not_called()

    @patch("app.routers.user_login_router.hash_str")
    @patch("app.routers.user_login_router.Repository")
    @patch("app.routers.user_login_router.Hook")
    async def test_login_attempts_limit(self, HookMock, RepositoryMock,
                                        hash_str_mock):
        schema_mock = AsyncMock(username="username", password="password")
        session_mock = AsyncMock()
        cache_mock = AsyncMock()

        hook_mock = AsyncMock()
        HookMock.return_value = hook_mock

        user_mock = AsyncMock(
            id=123, suspended_date=0, is_active=True, password_hash="hash",
            password_attempts=cfg.USER_PASSWORD_ATTEMPTS)

        repository_mock = AsyncMock()
        repository_mock.select.return_value = user_mock
        RepositoryMock.return_value = repository_mock

        with self.assertRaises(E) as context:
            await user_login(
                schema=schema_mock, session=session_mock, cache=cache_mock)

        self.assertEqual(user_mock.password_attempts, 0)
        self.assertTrue(user_mock.suspended_date > 0)
        repository_mock.update.assert_called_with(user_mock)

        self.assertEqual(context.exception.status_code, 422)
        self.assertEqual(context.exception.detail[0]["type"], "value_error")
        self.assertTrue("password" in context.exception.detail[0]["loc"])

        HookMock.assert_not_called()
        hook_mock.call.assert_not_called()

    @patch("app.routers.user_login_router.hash_str")
    @patch("app.routers.user_login_router.ctx")
    @patch("app.routers.user_login_router.Repository")
    @patch("app.routers.user_login_router.Hook")
    async def test_login_success(self, HookMock, RepositoryMock, ctx_mock,
                                 hash_str_mock):
        schema_mock = AsyncMock(username="username", password="password")
        session_mock = AsyncMock()
        cache_mock = AsyncMock()
        hash_str_mock.return_value = "hash"

        hook_mock = AsyncMock()
        HookMock.return_value = hook_mock

        user_mock = AsyncMock(id=123, suspended_date=0, is_active=True,
                              password_hash="hash", password_attempts=1)

        user_repository_mock = AsyncMock()
        user_repository_mock.select.return_value = user_mock

        RepositoryMock.return_value = user_repository_mock

        result = await user_login(
            schema=schema_mock, session=session_mock, cache=cache_mock)

        self.assertEqual(result, {"password_accepted": True})

        self.assertTrue(user_mock.password_accepted)
        self.assertEqual(user_mock.password_attempts, 0)
        user_repository_mock.update.assert_called_with(user_mock, commit=False)

        HookMock.assert_called_with(session_mock, cache_mock,
                                    current_user=user_mock)
        hook_mock.call.assert_called_with(HOOK_AFTER_USER_LOGIN)


if __name__ == "__main__":
    unittest.main()
