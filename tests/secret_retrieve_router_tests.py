import unittest
from unittest.mock import AsyncMock, MagicMock, patch
from app.routers.secret_retrieve_router import secret_retrieve
from app.hook import HOOK_AFTER_SECRET_RETRIEVE
from app.models.user_model import User
from app.config import get_config

cfg = get_config()


class SecretRetrieveRouterTest(unittest.IsolatedAsyncioTestCase):

    @patch("app.routers.secret_retrieve_router.os")
    @patch("app.routers.secret_retrieve_router.secret_read")
    @patch("app.routers.secret_retrieve_router.Hook")
    async def test_secret_retrieve(self, HookMock, secret_read_mock, os_mock):
        request_mock = MagicMock()
        session_mock = AsyncMock()
        cache_mock = AsyncMock()
        current_user_mock = AsyncMock(spec=User)
        secret_read_mock.return_value = "secret-key"
        os_mock.path.getctime.return_value = 123456

        hook_mock = AsyncMock()
        HookMock.return_value = hook_mock

        result = await secret_retrieve(
            request_mock, session=session_mock, cache=cache_mock,
            current_user=current_user_mock)

        self.assertEqual(result, {
            "created_date": os_mock.path.getctime.return_value,
            "secret_key": "secret-key",
            "secret_path": cfg.SECRET_KEY_PATH,
        })

        os_mock.path.getctime.assert_called_with(cfg.SECRET_KEY_PATH)
        HookMock.assert_called_with(
            request_mock.app, session_mock, cache_mock,
            current_user=current_user_mock)
        hook_mock.call.assert_called_with(
            HOOK_AFTER_SECRET_RETRIEVE, "secret-key", cfg.SECRET_KEY_PATH,
            os_mock.path.getctime.return_value)


if __name__ == "__main__":
    unittest.main()
