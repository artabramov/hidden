import unittest
import time
from unittest.mock import AsyncMock, MagicMock, patch
from app.routers.user_login import user_login
from app.hook import HOOK_AFTER_USER_LOGIN
from app.config import get_config
from app.error import E

cfg = get_config()


def _make_request_mock():
    req = MagicMock()
    req.app = MagicMock()
    req.app.state = MagicMock()
    req.app.state.config = cfg
    req.state = MagicMock()
    req.state.secret_key = "test-secret-key"
    req.state.log = MagicMock()
    req.state.log.debug = MagicMock()
    return req


def _make_schema_mock(username="username", password="password"):
    schema = MagicMock()
    schema.username = username
    secret = MagicMock()
    secret.get_secret_value.return_value = password
    schema.password = secret
    return schema


class UserLoginRouterTest(unittest.IsolatedAsyncioTestCase):

    @patch("app.routers.user_login.Hook")
    @patch("app.routers.user_login.Repository")
    @patch("app.routers.user_login.EncryptionManager")
    async def test_login_user_not_found(self, EncryptionManagerMock,
                                        RepositoryMock, HookMock):
        request_mock = _make_request_mock()
        schema_mock = _make_schema_mock(username="username")
        session_mock = AsyncMock()
        cache_mock = AsyncMock()

        enc = MagicMock()
        enc.get_hash.return_value = "hashed"
        EncryptionManagerMock.return_value = enc

        repository_mock = AsyncMock()
        repository_mock.select.return_value = None
        RepositoryMock.return_value = repository_mock

        with self.assertRaises(E) as context:
            await user_login(
                request_mock, schema_mock, session=session_mock,
                cache=cache_mock
            )

        self.assertEqual(context.exception.status_code, 422)
        self.assertEqual(context.exception.detail[0]["type"], "value_invalid")
        self.assertIn("username", context.exception.detail[0]["loc"])

        repository_mock.select.assert_awaited_with(username__eq="username")
        HookMock.assert_not_called()
        repository_mock.update.assert_not_called()

    @patch("app.routers.user_login.Hook")
    @patch("app.routers.user_login.Repository")
    @patch("app.routers.user_login.EncryptionManager")
    async def test_login_user_suspended(self, EncryptionManagerMock,
                                        RepositoryMock, HookMock):
        request_mock = _make_request_mock()
        schema_mock = _make_schema_mock(username="username")
        session_mock = AsyncMock()
        cache_mock = AsyncMock()

        enc = MagicMock()
        enc.get_hash.return_value = "irrelevant"
        EncryptionManagerMock.return_value = enc

        suspended_until = int(time.time()) + 60
        user_mock = AsyncMock(id=123, suspended_until_date=suspended_until,
                              active=True)

        repository_mock = AsyncMock()
        repository_mock.select.return_value = user_mock
        RepositoryMock.return_value = repository_mock

        with self.assertRaises(E) as context:
            await user_login(
                request_mock, schema_mock, session=session_mock,
                cache=cache_mock
            )

        self.assertEqual(context.exception.status_code, 422)
        self.assertEqual(context.exception.detail[0]["type"], "user_suspended")
        self.assertIn("username", context.exception.detail[0]["loc"])

        HookMock.assert_not_called()
        repository_mock.update.assert_not_called()

    @patch("app.routers.user_login.Hook")
    @patch("app.routers.user_login.Repository")
    @patch("app.routers.user_login.EncryptionManager")
    async def test_login_user_inactive(self, EncryptionManagerMock,
                                       RepositoryMock, HookMock):
        request_mock = _make_request_mock()
        schema_mock = _make_schema_mock(username="username")
        session_mock = AsyncMock()
        cache_mock = AsyncMock()

        enc = MagicMock()
        enc.get_hash.return_value = "irrelevant"
        EncryptionManagerMock.return_value = enc

        user_mock = AsyncMock(id=123, suspended_until_date=0, active=False)

        repository_mock = AsyncMock()
        repository_mock.select.return_value = user_mock
        RepositoryMock.return_value = repository_mock

        with self.assertRaises(E) as context:
            await user_login(
                request_mock, schema_mock, session=session_mock,
                cache=cache_mock
            )

        self.assertEqual(context.exception.status_code, 422)
        self.assertEqual(context.exception.detail[0]["type"], "user_inactive")
        self.assertIn("username", context.exception.detail[0]["loc"])

        HookMock.assert_not_called()
        repository_mock.update.assert_not_called()

    @patch("app.routers.user_login.Hook")
    @patch("app.routers.user_login.Repository")
    @patch("app.routers.user_login.EncryptionManager")
    async def test_login_password_invalid(self, EncryptionManagerMock,
                                          RepositoryMock, HookMock):
        request_mock = _make_request_mock()
        schema_mock = _make_schema_mock(username="username", password="wrong")
        session_mock = AsyncMock()
        cache_mock = AsyncMock()

        enc = MagicMock()
        enc.get_hash.return_value = "wrong_hash"
        EncryptionManagerMock.return_value = enc

        user_mock = AsyncMock(
            id=123,
            suspended_until_date=0,
            active=True,
            password_hash="correct_hash",
            password_attempts=1,
        )

        repository_mock = AsyncMock()
        repository_mock.select.return_value = user_mock
        RepositoryMock.return_value = repository_mock

        with self.assertRaises(E) as context:
            await user_login(
                request_mock, schema_mock, session=session_mock,
                cache=cache_mock
            )

        self.assertEqual(user_mock.password_attempts, 2)
        self.assertEqual(user_mock.suspended_until_date, 0)
        repository_mock.update.assert_awaited_with(user_mock)

        self.assertEqual(context.exception.status_code, 422)
        self.assertEqual(context.exception.detail[0]["type"], "value_invalid")
        self.assertIn("password", context.exception.detail[0]["loc"])

        HookMock.assert_not_called()

    @patch("app.routers.user_login.Hook")
    @patch("app.routers.user_login.Repository")
    @patch("app.routers.user_login.EncryptionManager")
    async def test_login_attempts_limit(self, EncryptionManagerMock,
                                        RepositoryMock, HookMock):
        request_mock = _make_request_mock()
        schema_mock = _make_schema_mock(username="username", password="wrong")
        session_mock = AsyncMock()
        cache_mock = AsyncMock()

        enc = MagicMock()
        enc.get_hash.return_value = "wrong_hash"
        EncryptionManagerMock.return_value = enc

        user_mock = AsyncMock(
            id=123,
            suspended_until_date=0,
            active=True,
            password_hash="correct_hash",
            password_attempts=cfg.AUTH_PASSWORD_ATTEMPTS - 1,
        )

        repository_mock = AsyncMock()
        repository_mock.select.return_value = user_mock
        RepositoryMock.return_value = repository_mock

        now_before = int(time.time())

        with self.assertRaises(E) as context:
            await user_login(
                request_mock, schema_mock, session=session_mock,
                cache=cache_mock
            )

        self.assertEqual(user_mock.password_attempts, 0)
        self.assertTrue(user_mock.suspended_until_date >= (
            now_before + cfg.AUTH_SUSPENDED_TIME))
        repository_mock.update.assert_awaited_with(user_mock)

        self.assertEqual(context.exception.status_code, 422)
        self.assertEqual(context.exception.detail[0]["type"], "value_invalid")
        self.assertIn("password", context.exception.detail[0]["loc"])

        HookMock.assert_not_called()

    @patch("app.routers.user_login.Hook")
    @patch("app.routers.user_login.Repository")
    @patch("app.routers.user_login.EncryptionManager")
    async def test_login_success(self, EncryptionManagerMock, RepositoryMock,
                                 HookMock):
        request_mock = _make_request_mock()
        schema_mock = _make_schema_mock(username="username", password="ok")
        session_mock = AsyncMock()
        cache_mock = AsyncMock()

        enc = MagicMock()
        enc.get_hash.return_value = "hash"
        EncryptionManagerMock.return_value = enc

        user_mock = AsyncMock(
            id=123,
            suspended_until_date=0,
            active=True,
            password_hash="hash",
            password_attempts=2,
        )

        user_repository_mock = AsyncMock()
        user_repository_mock.select.return_value = user_mock
        RepositoryMock.return_value = user_repository_mock

        hook_mock = AsyncMock()
        HookMock.return_value = hook_mock

        result = await user_login(
            request_mock, schema_mock, session=session_mock, cache=cache_mock
        )

        self.assertEqual(result, {"user_id": 123, "password_accepted": True})
        self.assertTrue(user_mock.password_accepted)
        self.assertEqual(user_mock.password_attempts, 0)
        self.assertEqual(user_mock.suspended_until_date, 0)

        user_repository_mock.update.assert_awaited_with(user_mock)

        HookMock.assert_called_with(
            request_mock, session_mock, cache_mock, current_user=user_mock
        )
        hook_mock.call.assert_awaited_with(HOOK_AFTER_USER_LOGIN)

        request_mock.state.log.debug.assert_called()
