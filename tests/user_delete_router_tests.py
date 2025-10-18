import unittest
from unittest.mock import AsyncMock, MagicMock, patch
from app.config import get_config
from app.error import E
from app.hook import HOOK_AFTER_USER_DELETE
from app.routers.user_delete import user_delete

cfg = get_config()


def _make_request_mock():
    req = MagicMock()
    req.app = MagicMock()
    req.app.state = MagicMock()
    req.app.state.config = cfg
    req.state = MagicMock()
    req.state.log = MagicMock()
    return req


class UserDeleteRouterTest(unittest.IsolatedAsyncioTestCase):

    @patch("app.routers.user_delete.Hook")
    @patch("app.routers.user_delete.Repository")
    async def test_delete_success(self, RepositoryMock, HookMock):
        request = _make_request_mock()
        session = AsyncMock()
        cache = AsyncMock()
        current_user = AsyncMock(id=999)

        target_user = AsyncMock(id=123)

        repo = AsyncMock()
        repo.select.return_value = target_user
        RepositoryMock.return_value = repo

        hook = AsyncMock()
        HookMock.return_value = hook

        result = await user_delete(
            request, 123, session=session, cache=cache,
            current_user=current_user
        )

        self.assertEqual(result, {"user_id": 123})
        repo.select.assert_awaited_with(id=123)
        repo.delete.assert_awaited_with(target_user)

        HookMock.assert_called_with(request, session, cache,
                                    current_user=current_user)
        hook.call.assert_awaited_with(HOOK_AFTER_USER_DELETE, target_user)

    @patch("app.routers.user_delete.Hook")
    @patch("app.routers.user_delete.Repository")
    async def test_delete_not_found(self, RepositoryMock, HookMock):
        request = _make_request_mock()
        session = AsyncMock()
        cache = AsyncMock()
        current_user = AsyncMock(id=999)

        repo = AsyncMock()
        repo.select.return_value = None
        RepositoryMock.return_value = repo

        hook = AsyncMock()
        HookMock.return_value = hook

        with self.assertRaises(E) as ctx:
            await user_delete(
                request, 123, session=session, cache=cache,
                current_user=current_user
            )

        repo.select.assert_awaited_with(id=123)
        self.assertEqual(ctx.exception.status_code, 404)
        self.assertEqual(ctx.exception.detail[0]["type"], "value_not_found")
        self.assertIn("user_id", ctx.exception.detail[0]["loc"])

        repo.delete.assert_not_called()
        HookMock.assert_not_called()
        hook.call.assert_not_called()

    @patch("app.routers.user_delete.Hook")
    @patch("app.routers.user_delete.Repository")
    async def test_delete_self_forbidden(self, RepositoryMock, HookMock):
        request = _make_request_mock()
        session = AsyncMock()
        cache = AsyncMock()

        current_user = AsyncMock(id=123)

        repo = AsyncMock()
        RepositoryMock.return_value = repo

        hook = AsyncMock()
        HookMock.return_value = hook

        with self.assertRaises(E) as ctx:
            await user_delete(
                request, 123, session=session, cache=cache,
                current_user=current_user
            )

        repo.select.assert_not_called()
        repo.delete.assert_not_called()
        HookMock.assert_not_called()
        hook.call.assert_not_called()

        self.assertEqual(ctx.exception.status_code, 422)
        self.assertEqual(ctx.exception.detail[0]["type"], "value_invalid")
        self.assertIn("user_id", ctx.exception.detail[0]["loc"])

    @patch("app.routers.user_delete.Hook")
    @patch("app.routers.user_delete.Repository")
    async def test_delete_error_raises_422(self, RepositoryMock, HookMock):
        request = _make_request_mock()
        session = AsyncMock()
        cache = AsyncMock()
        current_user = AsyncMock(id=999)

        target_user = AsyncMock(id=123)

        repo = AsyncMock()
        repo.select.return_value = target_user
        repo.delete.side_effect = Exception("db delete failed")
        RepositoryMock.return_value = repo

        hook = AsyncMock()
        HookMock.return_value = hook

        with self.assertRaises(E) as ctx:
            await user_delete(
                request, 123, session=session, cache=cache,
                current_user=current_user
            )

        repo.select.assert_awaited_with(id=123)
        repo.delete.assert_awaited_with(target_user)

        self.assertEqual(ctx.exception.status_code, 422)
        self.assertEqual(ctx.exception.detail[0]["type"], "value_invalid")
        self.assertIn("user_id", ctx.exception.detail[0]["loc"])

        HookMock.assert_not_called()
        hook.call.assert_not_called()
