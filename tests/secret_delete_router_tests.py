import unittest
from unittest.mock import AsyncMock, MagicMock, patch
from app.routers.secret_delete_router import secret_delete
from app.hook import HOOK_AFTER_SECRET_DELETE
from app.models.user_model import User
from app.config import get_config

cfg = get_config()


class SecretDeleteRouterTest(unittest.IsolatedAsyncioTestCase):

    @patch("app.routers.secret_delete_router.FileManager")
    @patch("app.routers.secret_delete_router.Hook")
    async def test_secret_delete(self, HookMock, FileManagerMock):
        request_mock = MagicMock()
        session_mock = AsyncMock()
        cache_mock = AsyncMock()
        current_user_mock = AsyncMock(spec=User)
        FileManagerMock.delete = AsyncMock()

        hook_mock = AsyncMock()
        HookMock.return_value = hook_mock

        result = await secret_delete(
            request_mock, session=session_mock, cache=cache_mock,
            current_user=current_user_mock)

        self.assertEqual(result, {"secret_path": cfg.SECRET_KEY_PATH})

        HookMock.assert_called_with(
            request_mock.app, session_mock, cache_mock,
            current_user=current_user_mock)
        hook_mock.call.assert_called_with(
            HOOK_AFTER_SECRET_DELETE, cfg.SECRET_KEY_PATH)


if __name__ == "__main__":
    unittest.main()
