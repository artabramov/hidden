import unittest
import jwt
from unittest.mock import AsyncMock, MagicMock, patch
from app.routers.token_retrieve_router import token_retrieve
from app.hook import HOOK_AFTER_TOKEN_RETRIEVE
from app.config import get_config
from app.error import E

cfg = get_config()


class TokenRetrieveRouterTest(unittest.IsolatedAsyncioTestCase):

    @patch("app.routers.token_retrieve_router.hash_str")
    @patch("app.routers.token_retrieve_router.Repository")
    @patch("app.routers.token_retrieve_router.Hook")
    async def test_token_retrieve_user_not_found(
            self, HookMock, RepositoryMock, hash_str_mock):
        request_mock = MagicMock()
        schema_mock = AsyncMock(username="username")
        session_mock = AsyncMock()
        cache_mock = AsyncMock()

        hook_mock = AsyncMock()
        HookMock.return_value = hook_mock

        repository_mock = AsyncMock()
        repository_mock.select.return_value = None
        RepositoryMock.return_value = repository_mock

        with self.assertRaises(E) as context:
            await token_retrieve(
                request_mock, schema=schema_mock, session=session_mock,
                cache=cache_mock)

        self.assertEqual(context.exception.status_code, 422)
        self.assertEqual(context.exception.detail[0]["type"], "value_error")
        self.assertTrue("username" in context.exception.detail[0]["loc"])

        HookMock.assert_not_called()
        hook_mock.call.assert_not_called()

    @patch("app.routers.token_retrieve_router.hash_str")
    @patch("app.routers.token_retrieve_router.Repository")
    @patch("app.routers.token_retrieve_router.Hook")
    async def test_token_retrieve_user_inactive(self, HookMock, RepositoryMock,
                                                hash_str_mock):
        request_mock = MagicMock()
        schema_mock = AsyncMock(username="username")
        session_mock = AsyncMock()
        cache_mock = AsyncMock()

        hook_mock = AsyncMock()
        HookMock.return_value = hook_mock

        user_mock = AsyncMock(id=123, is_active=False)

        repository_mock = AsyncMock()
        repository_mock.select.return_value = user_mock
        RepositoryMock.return_value = repository_mock

        with self.assertRaises(E) as context:
            await token_retrieve(
                request_mock, schema=schema_mock, session=session_mock,
                cache=cache_mock)

        self.assertEqual(context.exception.status_code, 422)
        self.assertEqual(context.exception.detail[0]["type"], "user_inactive")
        self.assertTrue("username" in context.exception.detail[0]["loc"])

        HookMock.assert_not_called()
        hook_mock.call.assert_not_called()

    @patch("app.routers.token_retrieve_router.hash_str")
    @patch("app.routers.token_retrieve_router.Repository")
    @patch("app.routers.token_retrieve_router.Hook")
    async def test_token_retrieve_password_not_accepted(
            self, HookMock, RepositoryMock, hash_str_mock):
        request_mock = MagicMock()
        schema_mock = AsyncMock(username="username", user_totp="123456")
        session_mock = AsyncMock()
        cache_mock = AsyncMock()

        hook_mock = AsyncMock()
        HookMock.return_value = hook_mock

        user_mock = AsyncMock(id=123, is_active=True, password_accepted=False,
                              user_totp="123456")

        repository_mock = AsyncMock()
        repository_mock.select.return_value = user_mock
        RepositoryMock.return_value = repository_mock

        with self.assertRaises(E) as context:
            await token_retrieve(
                request_mock, schema=schema_mock, session=session_mock,
                cache=cache_mock)

        self.assertEqual(context.exception.status_code, 422)
        self.assertEqual(context.exception.detail[0]["type"], "user_not_logged_in")  # noqa E501
        self.assertTrue("username" in context.exception.detail[0]["loc"])

        HookMock.assert_not_called()
        hook_mock.call.assert_not_called()

    @patch("app.routers.token_retrieve_router.hash_str")
    @patch("app.routers.token_retrieve_router.Repository")
    @patch("app.routers.token_retrieve_router.Hook")
    async def test_token_retrieve_totp_invalid(self, HookMock, RepositoryMock,
                                               hash_str_mock):
        request_mock = MagicMock()
        schema_mock = AsyncMock(username="username", user_totp="123456")
        session_mock = AsyncMock()
        cache_mock = AsyncMock()

        hook_mock = AsyncMock()
        HookMock.return_value = hook_mock

        user_mock = AsyncMock(id=123, is_active=True, password_accepted=True,
                              user_totp="456789", mfa_attempts=1)

        repository_mock = AsyncMock()
        repository_mock.select.return_value = user_mock
        RepositoryMock.return_value = repository_mock

        with self.assertRaises(E) as context:
            await token_retrieve(
                request_mock, schema=schema_mock, session=session_mock,
                cache=cache_mock)

        self.assertEqual(user_mock.mfa_attempts, 2)
        self.assertTrue(user_mock.password_accepted)
        repository_mock.update.assert_called_with(user_mock)

        self.assertEqual(context.exception.status_code, 422)
        self.assertEqual(context.exception.detail[0]["type"], "value_error")
        self.assertTrue("user_totp" in context.exception.detail[0]["loc"])

        HookMock.assert_not_called()
        hook_mock.call.assert_not_called()

    @patch("app.routers.token_retrieve_router.hash_str")
    @patch("app.routers.token_retrieve_router.Repository")
    @patch("app.routers.token_retrieve_router.Hook")
    async def test_token_retrieve_attempts_limit(
            self, HookMock, RepositoryMock, hash_str_mock):
        request_mock = MagicMock()
        schema_mock = AsyncMock(username="username", user_totp="123456")
        session_mock = AsyncMock()
        cache_mock = AsyncMock()

        hook_mock = AsyncMock()
        HookMock.return_value = hook_mock

        user_mock = AsyncMock(id=123, is_active=True, password_accepted=True,
                              user_totp="456789",
                              mfa_attempts=cfg.USER_TOTP_ATTEMPTS)

        repository_mock = AsyncMock()
        repository_mock.select.return_value = user_mock
        RepositoryMock.return_value = repository_mock

        with self.assertRaises(E) as context:
            await token_retrieve(
                request_mock, schema=schema_mock, session=session_mock,
                cache=cache_mock)

        self.assertEqual(user_mock.mfa_attempts, 0)
        self.assertFalse(user_mock.password_accepted)
        repository_mock.update.assert_called_with(user_mock)

        self.assertEqual(context.exception.status_code, 422)
        self.assertEqual(context.exception.detail[0]["type"], "value_error")
        self.assertTrue("user_totp" in context.exception.detail[0]["loc"])

        HookMock.assert_not_called()
        hook_mock.call.assert_not_called()

    @patch("app.routers.token_retrieve_router.hash_str")
    @patch("app.routers.token_retrieve_router.Repository")
    @patch("app.routers.token_retrieve_router.Hook")
    async def test_token_retrieve_success(self, HookMock, RepositoryMock,
                                          hash_str_mock):
        request_mock = MagicMock()
        schema_mock = AsyncMock(
            username="username", user_totp="123456", token_exp=None)
        session_mock = AsyncMock()
        cache_mock = AsyncMock()

        hook_mock = AsyncMock()
        HookMock.return_value = hook_mock

        user_mock = AsyncMock(id=123, is_active=True, password_accepted=True,
                              mfa_attempts=2, user_totp="123456", jti="jti",
                              user_role="reader", username="johndoe")

        repository_mock = AsyncMock()
        repository_mock.select.return_value = user_mock
        RepositoryMock.return_value = repository_mock

        result = await token_retrieve(
            request_mock, schema=schema_mock, session=session_mock,
            cache=cache_mock)

        token = result["user_token"]
        token_payload = jwt.decode(
            token, cfg.JWT_SECRET, algorithms=cfg.JWT_ALGORITHM)

        self.assertEqual(len(token_payload), 5)
        self.assertEqual(token_payload["user_id"], 123)
        self.assertEqual(token_payload["user_role"], "reader")
        self.assertEqual(token_payload["username"], "johndoe")
        self.assertEqual(token_payload["jti"], "jti")
        self.assertTrue(isinstance(token_payload["iat"], int))

        self.assertEqual(user_mock.mfa_attempts, 0)
        self.assertFalse(user_mock.password_accepted)
        repository_mock.update.assert_called_with(user_mock)

        HookMock.assert_called_with(request_mock.app, session_mock, cache_mock,
                                    current_user=user_mock)
        hook_mock.call.assert_called_with(HOOK_AFTER_TOKEN_RETRIEVE)


if __name__ == "__main__":
    unittest.main()
