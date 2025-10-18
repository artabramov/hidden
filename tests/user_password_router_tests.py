import unittest
from unittest.mock import AsyncMock, MagicMock, patch
from app.config import get_config
from app.error import E
from app.hook import HOOK_AFTER_USER_PASSWORD
from app.routers.user_password import User as UserModel
from app.routers.user_password import user_password

cfg = get_config()


def _req():
    req = MagicMock()
    req.app = MagicMock()
    req.app.state = MagicMock()
    req.app.state.config = cfg
    req.state = MagicMock()
    req.state.gocryptfs_key = "test-gocryptfs-key"
    req.state.log = MagicMock()
    return req


class UserPasswordRouterTest(unittest.IsolatedAsyncioTestCase):

    @patch("app.routers.user_password.EncryptionManager")
    @patch("app.routers.user_password.Repository")
    @patch("app.routers.user_password.Hook")
    async def test_change_password_success(self, HookMock, RepositoryMock,
                                           EncMgrMock):
        request = _req()
        session = AsyncMock()
        cache = AsyncMock()
        current_user = AsyncMock(id=123, password_hash="cur_hash")

        enc = MagicMock()
        enc.get_hash.side_effect = (
            lambda s: "cur_hash" if s == "OldP@ss1" else "new_hash")
        EncMgrMock.return_value = enc

        repo = AsyncMock()
        RepositoryMock.return_value = repo

        hook = AsyncMock()
        HookMock.return_value = hook

        class Schema:
            current_password = "OldP@ss1"
            updated_password = "NewP@ss1"

        result = await user_password(
            request, Schema(), 123, session=session, cache=cache,
            current_user=current_user
        )

        self.assertEqual(result, {"user_id": 123})
        self.assertEqual(current_user.password_hash, "new_hash")

        EncMgrMock.assert_called_once_with(cfg, "test-gocryptfs-key")
        RepositoryMock.assert_called_once_with(session, cache, UserModel, cfg)
        repo.update.assert_awaited_with(current_user)

        HookMock.assert_called_with(request, session, cache,
                                    current_user=current_user)
        hook.call.assert_awaited_with(HOOK_AFTER_USER_PASSWORD)

    @patch("app.routers.user_password.EncryptionManager")
    @patch("app.routers.user_password.Repository")
    @patch("app.routers.user_password.Hook")
    async def test_path_user_mismatch_422(self, HookMock, RepositoryMock,
                                          EncMgrMock):
        request = _req()
        session = AsyncMock()
        cache = AsyncMock()
        current_user = AsyncMock(id=999)

        class Schema:
            current_password = "OldP@ss1"
            updated_password = "NewP@ss1"

        with self.assertRaises(E) as ctx:
            await user_password(
                request, Schema(), 123, session=session, cache=cache,
                current_user=current_user
            )

        self.assertEqual(ctx.exception.status_code, 422)
        self.assertEqual(ctx.exception.detail[0]["type"], "value_invalid")
        self.assertIn("user_id", ctx.exception.detail[0]["loc"])

        EncMgrMock.assert_not_called()
        RepositoryMock.assert_not_called()
        HookMock.assert_not_called()

    @patch("app.routers.user_password.EncryptionManager")
    @patch("app.routers.user_password.Repository")
    @patch("app.routers.user_password.Hook")
    async def test_wrong_current_password_422(self, HookMock, RepositoryMock,
                                              EncMgrMock):
        request = _req()
        session = AsyncMock()
        cache = AsyncMock()
        current_user = AsyncMock(id=123, password_hash="cur_hash")

        enc = MagicMock()
        enc.get_hash.return_value = "wrong_hash"
        EncMgrMock.return_value = enc

        class Schema:
            current_password = "bad"
            updated_password = "NewP@ss1"

        with self.assertRaises(E) as ctx:
            await user_password(
                request, Schema(), 123, session=session, cache=cache,
                current_user=current_user
            )

        self.assertEqual(ctx.exception.status_code, 422)
        self.assertEqual(ctx.exception.detail[0]["type"], "value_invalid")
        self.assertIn("current_password", ctx.exception.detail[0]["loc"])

        RepositoryMock.assert_not_called()
        HookMock.assert_not_called()

    @patch("app.routers.user_password.EncryptionManager")
    @patch("app.routers.user_password.Repository")
    @patch("app.routers.user_password.Hook")
    async def test_same_password_422(self, HookMock, RepositoryMock,
                                     EncMgrMock):
        request = _req()
        session = AsyncMock()
        cache = AsyncMock()
        current_user = AsyncMock(id=123, password_hash="cur_hash")

        enc = MagicMock()
        enc.get_hash.return_value = "cur_hash"
        EncMgrMock.return_value = enc

        class Schema:
            current_password = "SameP@ss1"
            updated_password = "SameP@ss1"

        with self.assertRaises(E) as ctx:
            await user_password(
                request, Schema(), 123, session=session, cache=cache,
                current_user=current_user
            )

        self.assertEqual(ctx.exception.status_code, 422)
        self.assertEqual(ctx.exception.detail[0]["type"], "value_invalid")
        self.assertIn("updated_password", ctx.exception.detail[0]["loc"])

        RepositoryMock.assert_not_called()
        HookMock.assert_not_called()
