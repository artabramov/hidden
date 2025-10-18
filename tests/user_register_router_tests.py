import unittest
from unittest.mock import AsyncMock, MagicMock, patch
from app.models.user import UserRole
from app.routers.user_register import user_register
from app.hook import HOOK_AFTER_USER_REGISTER
from app.config import get_config
from app.error import E

cfg = get_config()


class UserRegisterRouterTest(unittest.IsolatedAsyncioTestCase):

    def _make_request_mock(self):
        req = MagicMock()
        req.app = MagicMock()
        req.app.state = MagicMock()
        req.app.state.config = cfg
        req.state = MagicMock()
        req.state.gocryptfs_key = "test-gocryptfs-key"
        req.state.log = MagicMock()
        return req

    def _make_schema_mock(
        self,
        username="username",
        password="password123!",
        first_name="John",
        last_name="Doe",
        summary="lorem ipsum",
    ):
        schema = MagicMock()
        schema.username = username
        schema.first_name = first_name
        schema.last_name = last_name
        schema.summary = summary
        secret = MagicMock()
        secret.get_secret_value.return_value = password
        schema.password = secret
        return schema

    @patch("app.routers.user_register.Hook")
    @patch("app.routers.user_register.Repository")
    @patch("app.routers.user_register.EncryptionManager")
    @patch("app.routers.user_register.generate_mfa_secret")
    @patch("app.routers.user_register.generate_jti")
    async def test_username_exists(
        self,
        gen_jti_mock,
        gen_mfa_mock,
        EncryptionManagerMock,
        RepositoryMock,
        HookMock,
    ):
        request_mock = self._make_request_mock()
        schema_mock = self._make_schema_mock(username="username")
        session_mock = AsyncMock()
        cache_mock = AsyncMock()

        repository_mock = AsyncMock()
        repository_mock.exists.return_value = True
        RepositoryMock.return_value = repository_mock

        with self.assertRaises(E) as context:
            await user_register(
                request_mock,
                schema_mock,
                session=session_mock,
                cache=cache_mock,
            )

        self.assertEqual(context.exception.status_code, 422)
        self.assertEqual(context.exception.detail[0]["type"], "value_exists")
        self.assertIn("username", context.exception.detail[0]["loc"])

        EncryptionManagerMock.assert_called_once_with(
            request_mock.app.state.config,
            request_mock.state.gocryptfs_key
        )

        HookMock.assert_not_called()
        gen_jti_mock.assert_not_called()
        gen_mfa_mock.assert_not_called()
        repository_mock.insert.assert_not_called()

    @patch("app.routers.user_register.Hook")
    @patch("app.routers.user_register.Repository")
    @patch("app.routers.user_register.User")
    @patch("app.routers.user_register.EncryptionManager")
    @patch("app.routers.user_register.generate_mfa_secret")
    @patch("app.routers.user_register.generate_jti")
    async def test_register_reader(
        self,
        gen_jti_mock,
        gen_mfa_mock,
        EncryptionManagerMock,
        UserMock,
        RepositoryMock,
        HookMock,
    ):
        request_mock = self._make_request_mock()
        schema_mock = self._make_schema_mock(
            username="username",
            password="P@ssw0rd!",
            first_name="John",
            last_name="Doe",
            summary="lorem ipsum",
        )
        session_mock = AsyncMock()
        cache_mock = AsyncMock()

        gen_jti_mock.return_value = "JTI123"
        gen_mfa_mock.return_value = "MFA123"

        enc = MagicMock()
        enc.get_hash.return_value = "HASHED_PASSWORD"
        enc.encrypt_str.side_effect = lambda s: f"enc({s})"
        EncryptionManagerMock.return_value = enc

        repository_mock = AsyncMock()
        repository_mock.exists.return_value = False
        repository_mock.count_all.return_value = 1
        RepositoryMock.return_value = repository_mock

        hook_mock = AsyncMock()
        HookMock.return_value = hook_mock

        result = await user_register(
            request_mock,
            schema_mock,
            session=session_mock,
            cache=cache_mock,
        )

        self.assertDictEqual(
            result,
            {
                "user_id": UserMock.return_value.id,
                "mfa_secret": "MFA123",
            },
        )

        UserMock.assert_called_with(
            schema_mock.username,
            "HASHED_PASSWORD",
            schema_mock.first_name,
            schema_mock.last_name,
            UserRole.reader,
            False,
            "enc(MFA123)",
            "enc(JTI123)",
            summary=schema_mock.summary,
        )

        repository_mock.exists.assert_awaited_with(
            username__eq=schema_mock.username)
        repository_mock.count_all.assert_awaited()
        repository_mock.insert.assert_awaited_with(UserMock.return_value)

        HookMock.assert_called_with(
            request_mock,
            session_mock,
            cache_mock,
            current_user=UserMock.return_value,
        )
        hook_mock.call.assert_awaited_with(HOOK_AFTER_USER_REGISTER)

    @patch("app.routers.user_register.Hook")
    @patch("app.routers.user_register.Repository")
    @patch("app.routers.user_register.User")
    @patch("app.routers.user_register.EncryptionManager")
    @patch("app.routers.user_register.generate_mfa_secret")
    @patch("app.routers.user_register.generate_jti")
    async def test_register_admin(
        self,
        gen_jti_mock,
        gen_mfa_mock,
        EncryptionManagerMock,
        UserMock,
        RepositoryMock,
        HookMock,
    ):
        request_mock = self._make_request_mock()
        schema_mock = self._make_schema_mock(
            username="username",
            password="P@ssw0rd!",
            first_name="John",
            last_name="Doe",
            summary="lorem ipsum",
        )
        session_mock = AsyncMock()
        cache_mock = AsyncMock()

        gen_jti_mock.return_value = "JTI123"
        gen_mfa_mock.return_value = "MFA123"

        enc = MagicMock()
        enc.get_hash.return_value = "HASHED_PASSWORD"
        enc.encrypt_str.side_effect = lambda s: f"enc({s})"
        EncryptionManagerMock.return_value = enc

        repository_mock = AsyncMock()
        repository_mock.exists.return_value = False
        repository_mock.count_all.return_value = 0
        RepositoryMock.return_value = repository_mock

        hook_mock = AsyncMock()
        HookMock.return_value = hook_mock

        result = await user_register(
            request_mock,
            schema_mock,
            session=session_mock,
            cache=cache_mock,
        )

        self.assertDictEqual(
            result,
            {
                "user_id": UserMock.return_value.id,
                "mfa_secret": "MFA123",
            },
        )

        UserMock.assert_called_with(
            schema_mock.username,
            "HASHED_PASSWORD",
            schema_mock.first_name,
            schema_mock.last_name,
            UserRole.admin,
            True,  # active
            "enc(MFA123)",
            "enc(JTI123)",
            summary=schema_mock.summary,
        )

        repository_mock.insert.assert_awaited_with(UserMock.return_value)

        HookMock.assert_called_with(
            request_mock,
            session_mock,
            cache_mock,
            current_user=UserMock.return_value,
        )
        hook_mock.call.assert_awaited_with(HOOK_AFTER_USER_REGISTER)
