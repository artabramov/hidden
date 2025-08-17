import unittest
from unittest.mock import AsyncMock, MagicMock, patch
from app.routers.token_invalidate_router import token_invalidate
from app.hook import HOOK_AFTER_TOKEN_INVALIDATE
from app.models.user_model import User


class TokenInvalidateRouterTest(unittest.IsolatedAsyncioTestCase):

    @patch("app.routers.token_invalidate_router.generate_jti")
    @patch("app.routers.token_invalidate_router.Hook")
    @patch("app.routers.token_invalidate_router.Repository")
    async def test_token_invalidate(self, RepositoryMock, HookMock,
                                    generate_jti_mock):
        request_mock = MagicMock()
        session_mock = AsyncMock()
        cache_mock = AsyncMock()
        generate_jti_mock.return_value = "jti"

        current_user_mock = AsyncMock(spec=User)
        current_user_mock.id = 123

        repository_mock = AsyncMock()
        RepositoryMock.return_value = repository_mock

        hook_mock = AsyncMock()
        HookMock.return_value = hook_mock

        result = await token_invalidate(
            request_mock, session=session_mock, cache=cache_mock,
            current_user=current_user_mock)

        self.assertEqual(result, {"user_id": 123})
        generate_jti_mock.assert_called_once()
        repository_mock.update.assert_called_with(current_user_mock)
        self.assertEqual(current_user_mock.jti, "jti")

        HookMock.assert_called_with(request_mock.app, session_mock, cache_mock,
                                    current_user=current_user_mock)
        hook_mock.call.assert_called_with(HOOK_AFTER_TOKEN_INVALIDATE)


if __name__ == "__main__":
    unittest.main()
