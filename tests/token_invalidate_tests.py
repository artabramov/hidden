import unittest
from unittest.mock import AsyncMock, MagicMock, patch
from app.routers.token_invalidate import token_invalidate
from app.hook import HOOK_AFTER_TOKEN_INVALIDATE
from app.models.user import User
from app.config import get_config

cfg = get_config()


def _make_request_mock():
    req = MagicMock()
    req.app = MagicMock()
    req.app.state = MagicMock()
    req.app.state.config = cfg
    req.state = MagicMock()
    req.state.gocryptfs_key = "test-gocryptfs-key"
    req.state.log = MagicMock()
    return req


class TokenInvalidateRouterTest(unittest.IsolatedAsyncioTestCase):

    @patch("app.routers.token_invalidate.EncryptionManager")
    @patch("app.routers.token_invalidate.Repository")
    @patch("app.routers.token_invalidate.Hook")
    @patch("app.routers.token_invalidate.generate_jti")
    async def test_token_invalidate(
        self, generate_jti_mock, HookMock, RepositoryMock,
        EncryptionManagerMock
    ):
        request_mock = _make_request_mock()
        session_mock = AsyncMock()
        cache_mock = AsyncMock()

        generate_jti_mock.return_value = "JTI123"
        enc = MagicMock()
        enc.encrypt_str.side_effect = lambda s: f"enc({s})"
        EncryptionManagerMock.return_value = enc

        current_user_mock = AsyncMock(spec=User)
        current_user_mock.id = 123
        current_user_mock.jti_encrypted = None

        repository_mock = AsyncMock()
        RepositoryMock.return_value = repository_mock

        hook_mock = AsyncMock()
        HookMock.return_value = hook_mock

        result = await token_invalidate(
            request_mock, session=session_mock, cache=cache_mock,
            current_user=current_user_mock
        )

        self.assertEqual(result, {"user_id": 123})

        generate_jti_mock.assert_called_once()
        EncryptionManagerMock.assert_called_once_with(
            cfg, "test-gocryptfs-key")
        enc.encrypt_str.assert_called_once_with("JTI123")
        self.assertEqual(current_user_mock.jti_encrypted, "enc(JTI123)")

        repository_mock.update.assert_awaited_with(current_user_mock)

        HookMock.assert_called_with(
            request_mock, session_mock, cache_mock,
            current_user=current_user_mock
        )
        hook_mock.call.assert_awaited_with(HOOK_AFTER_TOKEN_INVALIDATE)
