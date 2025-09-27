import unittest
from unittest.mock import AsyncMock, MagicMock, patch
from app.routers.user_select import user_select
from app.hook import HOOK_AFTER_USER_SELECT
from app.error import E
from app.config import get_config


def _make_request_mock():
    req = MagicMock()
    req.app = MagicMock()
    req.app.state = MagicMock()
    req.app.state.config = get_config()
    req.state = MagicMock()
    req.state.log = MagicMock()
    req.state.log.debug = MagicMock()
    return req


class UserSelectRouterTest(unittest.IsolatedAsyncioTestCase):

    @patch("app.routers.user_select.Hook")
    @patch("app.routers.user_select.Repository")
    async def test_user_select_success(self, RepositoryMock, HookMock):
        request = _make_request_mock()
        session = AsyncMock()
        cache = AsyncMock()
        current_user = AsyncMock()

        user = AsyncMock(id=123)
        user.to_dict = AsyncMock(
            return_value={"id": 123, "username": "johndoe"})

        repo = AsyncMock()
        repo.select.return_value = user
        RepositoryMock.return_value = repo

        hook = AsyncMock()
        HookMock.return_value = hook

        result = await user_select(
            request, 123, session=session, cache=cache,
            current_user=current_user
        )

        self.assertEqual(result, {"id": 123, "username": "johndoe"})
        repo.select.assert_awaited_with(id=123)

        HookMock.assert_called_with(request, session, cache,
                                    current_user=current_user)
        hook.call.assert_awaited_with(HOOK_AFTER_USER_SELECT, user)

        request.state.log.debug.assert_called()

    @patch("app.routers.user_select.Hook")
    @patch("app.routers.user_select.Repository")
    async def test_user_select_not_found(self, RepositoryMock, HookMock):
        request = _make_request_mock()
        session = AsyncMock()
        cache = AsyncMock()

        repo = AsyncMock()
        repo.select.return_value = None
        RepositoryMock.return_value = repo

        hook = AsyncMock()
        HookMock.return_value = hook

        with self.assertRaises(E) as ctx:
            await user_select(request, 123, session=session, cache=cache)

        repo.select.assert_awaited_with(id=123)

        self.assertEqual(ctx.exception.status_code, 404)
        self.assertEqual(ctx.exception.detail[0]["type"], "value_not_found")
        self.assertIn("user_id", ctx.exception.detail[0]["loc"])

        HookMock.assert_not_called()
        hook.call.assert_not_called()
