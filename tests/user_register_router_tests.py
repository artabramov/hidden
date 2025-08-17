import unittest
from unittest.mock import AsyncMock, patch
from app.models.user_model import UserRole
from app.routers.user_register_router import user_register
from app.hook import HOOK_AFTER_USER_REGISTER
from app.config import get_config
from app.error import E

cfg = get_config()


class UserRegisterRouterTest(unittest.IsolatedAsyncioTestCase):

    @patch("app.routers.user_register_router.hash_str")
    @patch("app.routers.user_register_router.Repository")
    @patch("app.routers.user_register_router.Hook")
    async def test_username_exists(self, HookMock, RepositoryMock,
                                   hash_str_mock):
        schema_mock = AsyncMock(username="username", password="password")
        session_mock = AsyncMock()
        cache_mock = AsyncMock()

        hook_mock = AsyncMock()
        HookMock.return_value = hook_mock

        repository_mock = AsyncMock()
        repository_mock.exists.return_value = True
        RepositoryMock.return_value = repository_mock

        with self.assertRaises(E) as context:
            await user_register(
                schema=schema_mock, session=session_mock, cache=cache_mock)

        self.assertEqual(context.exception.status_code, 422)
        self.assertEqual(context.exception.detail[0]["type"], "value_exists")
        self.assertTrue("username" in context.exception.detail[0]["loc"])

        HookMock.assert_not_called()
        hook_mock.call.assert_not_called()

    @patch("app.routers.user_register_router.hash_str")
    @patch("app.routers.user_register_router.User")
    @patch("app.routers.user_register_router.Repository")
    @patch("app.routers.user_register_router.Hook")
    async def test_register_reader(self, HookMock, RepositoryMock, UserMock,
                                   hash_str_mock):
        schema_mock = AsyncMock(
            username="username", password="password", first_name="John",
            last_name="Doe", user_summary="lorem ipsum")
        session_mock = AsyncMock()
        cache_mock = AsyncMock()

        hook_mock = AsyncMock()
        HookMock.return_value = hook_mock

        repository_mock = AsyncMock()
        repository_mock.exists.return_value = False
        repository_mock.count_all.return_value = 1
        RepositoryMock.return_value = repository_mock

        result = await user_register(
                schema=schema_mock, session=session_mock, cache=cache_mock)

        self.assertDictEqual(result, {
            "user_id": UserMock.return_value.id,
            "mfa_secret": UserMock.return_value.mfa_secret,
        })

        UserMock.assert_called_with(
            schema_mock.username, schema_mock.password, schema_mock.first_name,
            schema_mock.last_name, is_active=False, user_role=UserRole.reader,
            user_summary=schema_mock.user_summary)
        repository_mock.insert.assert_called_with(UserMock.return_value)

        HookMock.assert_called_with(session_mock, cache_mock,
                                    current_user=UserMock.return_value)
        hook_mock.call.assert_called_with(HOOK_AFTER_USER_REGISTER)

    @patch("app.routers.user_register_router.hash_str")
    @patch("app.routers.user_register_router.User")
    @patch("app.routers.user_register_router.Repository")
    @patch("app.routers.user_register_router.Hook")
    async def test_register_admin(self, HookMock, RepositoryMock, UserMock,
                                  hash_str_mock):
        schema_mock = AsyncMock(
            username="username", password="password", first_name="John",
            last_name="Doe", user_summary="lorem ipsum")
        session_mock = AsyncMock()
        cache_mock = AsyncMock()

        hook_mock = AsyncMock()
        HookMock.return_value = hook_mock

        repository_mock = AsyncMock()
        repository_mock.exists.return_value = False
        repository_mock.count_all.return_value = 0
        RepositoryMock.return_value = repository_mock

        result = await user_register(
                schema=schema_mock, session=session_mock, cache=cache_mock)

        self.assertDictEqual(result, {
            "user_id": UserMock.return_value.id,
            "mfa_secret": UserMock.return_value.mfa_secret,
        })

        UserMock.assert_called_with(
            schema_mock.username, schema_mock.password, schema_mock.first_name,
            schema_mock.last_name, is_active=True, user_role=UserRole.admin,
            user_summary=schema_mock.user_summary)
        repository_mock.insert.assert_called_with(UserMock.return_value)

        HookMock.assert_called_with(session_mock, cache_mock,
                                    current_user=UserMock.return_value)
        hook_mock.call.assert_called_with(HOOK_AFTER_USER_REGISTER)


if __name__ == "__main__":
    unittest.main()
