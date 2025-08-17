import unittest
from unittest.mock import AsyncMock, MagicMock, patch
from app.routers.lock_create_router import lock_create
from app.hook import HOOK_AFTER_LOCK_CREATE
from app.models.user_model import User


class LockCreateRouterTest(unittest.IsolatedAsyncioTestCase):

    @patch("app.routers.lock_create_router.lock_enable")
    @patch("app.routers.lock_create_router.Hook")
    async def test_lock_create(self, HookMock, lock_enable_mock):
        request_mock = MagicMock()
        session_mock = AsyncMock()
        cache_mock = AsyncMock()
        current_user_mock = AsyncMock(spec=User)

        hook_mock = AsyncMock()
        HookMock.return_value = hook_mock

        result = await lock_create(
            request_mock, session=session_mock, cache=cache_mock,
            current_user=current_user_mock)

        self.assertDictEqual(result, {"lock_exists": True})
        lock_enable_mock.assert_called_once()

        HookMock.assert_called_with(
            request_mock.app, session_mock, cache_mock,
            current_user=current_user_mock)
        hook_mock.call.assert_called_with(HOOK_AFTER_LOCK_CREATE)


if __name__ == "__main__":
    unittest.main()
