import unittest
from unittest.mock import AsyncMock, MagicMock, patch
from app.routers.token_retrieve import token_retrieve
from app.hook import HOOK_AFTER_TOKEN_RETRIEVE
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


def _make_schema_mock(username="username", totp="123456", exp=None):
    schema = MagicMock()
    schema.username = username
    schema.totp = totp
    schema.exp = exp
    return schema


class TokenRetrieveRouterTest(unittest.IsolatedAsyncioTestCase):

    @patch("app.routers.token_retrieve.encode_jwt")
    @patch("app.routers.token_retrieve.create_payload")
    @patch("app.routers.token_retrieve.calculate_totp")
    @patch("app.routers.token_retrieve.Hook")
    @patch("app.routers.token_retrieve.Repository")
    @patch("app.routers.token_retrieve.EncryptionManager")
    async def test_token_retrieve_user_not_found(
        self, EncryptionManagerMock, RepositoryMock, HookMock,
        calculate_totp_mock, create_payload_mock, encode_jwt_mock
    ):
        request_mock = _make_request_mock()
        schema_mock = _make_schema_mock(username="username")
        session_mock = AsyncMock()
        cache_mock = AsyncMock()

        enc = MagicMock()
        EncryptionManagerMock.return_value = enc

        repository_mock = AsyncMock()
        repository_mock.select.return_value = None
        RepositoryMock.return_value = repository_mock

        with self.assertRaises(E) as context:
            await token_retrieve(
                request_mock, schema=schema_mock, session=session_mock,
                cache=cache_mock
            )

        self.assertEqual(context.exception.status_code, 422)
        self.assertEqual(context.exception.detail[0]["type"], "value_invalid")
        self.assertIn("username", context.exception.detail[0]["loc"])

        repository_mock.select.assert_awaited_with(username__eq="username")
        HookMock.assert_not_called()
        repository_mock.update.assert_not_called()
        calculate_totp_mock.assert_not_called()
        create_payload_mock.assert_not_called()
        encode_jwt_mock.assert_not_called()

    @patch("app.routers.token_retrieve.encode_jwt")
    @patch("app.routers.token_retrieve.create_payload")
    @patch("app.routers.token_retrieve.calculate_totp")
    @patch("app.routers.token_retrieve.Hook")
    @patch("app.routers.token_retrieve.Repository")
    @patch("app.routers.token_retrieve.EncryptionManager")
    async def test_token_retrieve_user_inactive(
        self, EncryptionManagerMock, RepositoryMock, HookMock,
        calculate_totp_mock, create_payload_mock, encode_jwt_mock
    ):
        request_mock = _make_request_mock()
        schema_mock = _make_schema_mock(username="username")
        session_mock = AsyncMock()
        cache_mock = AsyncMock()

        enc = MagicMock()
        EncryptionManagerMock.return_value = enc

        user_mock = AsyncMock(id=123, active=False)
        repository_mock = AsyncMock()
        repository_mock.select.return_value = user_mock
        RepositoryMock.return_value = repository_mock

        with self.assertRaises(E) as context:
            await token_retrieve(
                request_mock, schema=schema_mock, session=session_mock,
                cache=cache_mock
            )

        self.assertEqual(context.exception.status_code, 422)
        self.assertEqual(context.exception.detail[0]["type"], "user_inactive")
        self.assertIn("username", context.exception.detail[0]["loc"])

        HookMock.assert_not_called()
        repository_mock.update.assert_not_called()
        calculate_totp_mock.assert_not_called()
        create_payload_mock.assert_not_called()
        encode_jwt_mock.assert_not_called()

    @patch("app.routers.token_retrieve.encode_jwt")
    @patch("app.routers.token_retrieve.create_payload")
    @patch("app.routers.token_retrieve.calculate_totp")
    @patch("app.routers.token_retrieve.Hook")
    @patch("app.routers.token_retrieve.Repository")
    @patch("app.routers.token_retrieve.EncryptionManager")
    async def test_token_retrieve_password_not_accepted(
        self, EncryptionManagerMock, RepositoryMock, HookMock,
        calculate_totp_mock, create_payload_mock, encode_jwt_mock
    ):
        request_mock = _make_request_mock()
        schema_mock = _make_schema_mock(username="username", totp="123456")
        session_mock = AsyncMock()
        cache_mock = AsyncMock()

        enc = MagicMock()
        EncryptionManagerMock.return_value = enc

        user_mock = AsyncMock(id=123, active=True, password_accepted=False)
        repository_mock = AsyncMock()
        repository_mock.select.return_value = user_mock
        RepositoryMock.return_value = repository_mock

        with self.assertRaises(E) as context:
            await token_retrieve(
                request_mock, schema=schema_mock, session=session_mock,
                cache=cache_mock
            )

        self.assertEqual(context.exception.status_code, 422)
        self.assertEqual(context.exception.detail[0]["type"],
                         "user_not_logged_in")
        self.assertIn("username", context.exception.detail[0]["loc"])

        HookMock.assert_not_called()
        repository_mock.update.assert_not_called()
        calculate_totp_mock.assert_not_called()
        create_payload_mock.assert_not_called()
        encode_jwt_mock.assert_not_called()

    @patch("app.routers.token_retrieve.encode_jwt")
    @patch("app.routers.token_retrieve.create_payload")
    @patch("app.routers.token_retrieve.calculate_totp")
    @patch("app.routers.token_retrieve.Hook")
    @patch("app.routers.token_retrieve.Repository")
    @patch("app.routers.token_retrieve.EncryptionManager")
    async def test_token_retrieve_totp_invalid(
        self, EncryptionManagerMock, RepositoryMock, HookMock,
        calculate_totp_mock, create_payload_mock, encode_jwt_mock
    ):
        request_mock = _make_request_mock()
        schema_mock = _make_schema_mock(username="username", totp="123456")
        session_mock = AsyncMock()
        cache_mock = AsyncMock()

        enc = MagicMock()
        enc.decrypt_str.return_value = "MFA_SECRET"
        EncryptionManagerMock.return_value = enc

        user_mock = AsyncMock(
            id=123, active=True, password_accepted=True, mfa_attempts=1,
            mfa_secret_encrypted="enc(secret)"
        )

        repository_mock = AsyncMock()
        repository_mock.select.return_value = user_mock
        RepositoryMock.return_value = repository_mock

        calculate_totp_mock.return_value = "654321"

        with self.assertRaises(E) as context:
            await token_retrieve(
                request_mock, schema=schema_mock, session=session_mock,
                cache=cache_mock
            )

        self.assertEqual(user_mock.mfa_attempts, 2)
        self.assertTrue(user_mock.password_accepted)
        repository_mock.update.assert_awaited_with(user_mock)

        self.assertEqual(context.exception.status_code, 422)
        self.assertEqual(context.exception.detail[0]["type"], "value_invalid")
        self.assertIn("totp", context.exception.detail[0]["loc"])

        HookMock.assert_not_called()
        create_payload_mock.assert_not_called()
        encode_jwt_mock.assert_not_called()

    @patch("app.routers.token_retrieve.encode_jwt")
    @patch("app.routers.token_retrieve.create_payload")
    @patch("app.routers.token_retrieve.calculate_totp")
    @patch("app.routers.token_retrieve.Hook")
    @patch("app.routers.token_retrieve.Repository")
    @patch("app.routers.token_retrieve.EncryptionManager")
    async def test_token_retrieve_attempts_limit(
        self, EncryptionManagerMock, RepositoryMock, HookMock,
        calculate_totp_mock, create_payload_mock, encode_jwt_mock
    ):
        request_mock = _make_request_mock()
        schema_mock = _make_schema_mock(username="username", totp="123456")
        session_mock = AsyncMock()
        cache_mock = AsyncMock()

        enc = MagicMock()
        enc.decrypt_str.return_value = "MFA_SECRET"
        EncryptionManagerMock.return_value = enc

        user_mock = AsyncMock(
            id=123, active=True, password_accepted=True,
            mfa_attempts=cfg.AUTH_TOTP_ATTEMPTS - 1,
            mfa_secret_encrypted="enc(secret)"
        )

        repository_mock = AsyncMock()
        repository_mock.select.return_value = user_mock
        RepositoryMock.return_value = repository_mock

        calculate_totp_mock.return_value = "000000"

        with self.assertRaises(E) as context:
            await token_retrieve(
                request_mock, schema=schema_mock, session=session_mock,
                cache=cache_mock
            )

        self.assertEqual(user_mock.mfa_attempts, 0)
        self.assertFalse(user_mock.password_accepted)
        repository_mock.update.assert_awaited_with(user_mock)

        self.assertEqual(context.exception.status_code, 422)
        self.assertEqual(context.exception.detail[0]["type"], "value_invalid")
        self.assertIn("totp", context.exception.detail[0]["loc"])

        HookMock.assert_not_called()
        create_payload_mock.assert_not_called()
        encode_jwt_mock.assert_not_called()

    @patch("app.routers.token_retrieve.encode_jwt")
    @patch("app.routers.token_retrieve.create_payload")
    @patch("app.routers.token_retrieve.calculate_totp")
    @patch("app.routers.token_retrieve.Hook")
    @patch("app.routers.token_retrieve.Repository")
    @patch("app.routers.token_retrieve.EncryptionManager")
    async def test_token_retrieve_success(
        self, EncryptionManagerMock, RepositoryMock, HookMock,
        calculate_totp_mock, create_payload_mock, encode_jwt_mock
    ):
        request_mock = _make_request_mock()
        schema_mock = _make_schema_mock(username="username", totp="123456",
                                        exp=None)
        session_mock = AsyncMock()
        cache_mock = AsyncMock()

        enc = MagicMock()
        def _decrypt(val):
            if val == "enc(mfa)":
                return "MFA_SECRET"
            if val == "enc(jti)":
                return "JTI123"
            return f"dec({val})"
        enc.decrypt_str.side_effect = _decrypt
        EncryptionManagerMock.return_value = enc

        user_mock = AsyncMock(
            id=123, active=True, password_accepted=True, mfa_attempts=2,
            mfa_secret_encrypted="enc(mfa)", jti_encrypted="enc(jti)"
        )

        repository_mock = AsyncMock()
        repository_mock.select.return_value = user_mock
        RepositoryMock.return_value = repository_mock

        calculate_totp_mock.return_value = "123456"

        create_payload_mock.return_value = {"k": "v"}
        encode_jwt_mock.return_value = "TOKEN123"

        hook_mock = AsyncMock()
        HookMock.return_value = hook_mock

        result = await token_retrieve(
            request_mock, schema=schema_mock, session=session_mock,
            cache=cache_mock
        )

        self.assertEqual(result, {"user_id": 123, "user_token": "TOKEN123"})

        self.assertEqual(user_mock.mfa_attempts, 0)
        self.assertFalse(user_mock.password_accepted)
        repository_mock.update.assert_awaited_with(user_mock)

        create_payload_mock.assert_called_once()
        args, kwargs = create_payload_mock.call_args
        self.assertIs(args[0], user_mock)
        self.assertEqual(args[1], "JTI123")
        self.assertIn("exp", kwargs)
        self.assertIsNone(kwargs["exp"])

        encode_jwt_mock.assert_called_once()
        _, enc_kwargs = encode_jwt_mock.call_args

        HookMock.assert_called_with(request_mock, session_mock, cache_mock,
                                    current_user=user_mock)
        hook_mock.call.assert_awaited_with(HOOK_AFTER_TOKEN_RETRIEVE)
        request_mock.state.log.debug.assert_called()
