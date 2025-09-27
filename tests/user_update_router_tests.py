import unittest
from unittest.mock import AsyncMock, MagicMock, patch
from app.config import get_config
from app.error import E
from app.hook import HOOK_AFTER_USER_UPDATE
from app.routers.user_update import user_update, User as UserModel

cfg = get_config()


def _req():
    r = MagicMock()
    r.app = MagicMock()
    r.app.state = MagicMock()
    r.app.state.config = cfg
    r.state = MagicMock()
    r.state.log = MagicMock()
    r.state.log.debug = MagicMock()
    return r


class UserUpdateRouterTest(unittest.IsolatedAsyncioTestCase):

    @patch("app.routers.user_update.Hook")
    @patch("app.routers.user_update.Repository")
    async def test_update_success(self, RepositoryMock, HookMock):
        request = _req()
        session = AsyncMock()
        cache = AsyncMock()

        current_user = AsyncMock(spec=UserModel)
        current_user.id = 123
        current_user.first_name = "Old"
        current_user.last_name = "Name"
        current_user.summary = None

        class Schema:
            first_name = "John"
            last_name = "Doe"
            summary = "hello"

        repo = AsyncMock()
        RepositoryMock.return_value = repo

        hook = AsyncMock()
        HookMock.return_value = hook

        result = await user_update(
            request, Schema(), 123, session=session, cache=cache,
            current_user=current_user
        )

        self.assertEqual(result, {"user_id": 123})
        self.assertEqual(current_user.first_name, "John")
        self.assertEqual(current_user.last_name, "Doe")
        self.assertEqual(current_user.summary, "hello")

        RepositoryMock.assert_called_once_with(session, cache, UserModel, cfg)
        repo.update.assert_awaited_with(current_user)

        HookMock.assert_called_with(request, session, cache,
                                    current_user=current_user)
        hook.call.assert_awaited_with(HOOK_AFTER_USER_UPDATE)

        request.state.log.debug.assert_called()

    @patch("app.routers.user_update.Hook")
    @patch("app.routers.user_update.Repository")
    async def test_update_path_mismatch(self, RepositoryMock, HookMock):
        request = _req()
        session = AsyncMock()
        cache = AsyncMock()

        current_user = AsyncMock(spec=UserModel)
        current_user.id = 999

        class Schema:
            first_name = "John"
            last_name = "Doe"
            summary = None

        with self.assertRaises(E) as ctx:
            await user_update(
                request, Schema(), 123, session=session, cache=cache,
                current_user=current_user
            )

        self.assertEqual(ctx.exception.status_code, 422)
        self.assertEqual(ctx.exception.detail[0]["type"], "value_invalid")
        self.assertIn("user_id", ctx.exception.detail[0]["loc"])

        RepositoryMock.assert_not_called()
        HookMock.assert_not_called()
