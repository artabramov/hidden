import unittest
from unittest.mock import MagicMock, AsyncMock, patch
from jwt.exceptions import ExpiredSignatureError, PyJWTError
from app.auth import auth, _can_read, _can_write, _can_edit, _can_admin, _auth
from app.models.user_model import UserRole
from app.error import E


class TestAuth(unittest.IsolatedAsyncioTestCase):

    @patch("app.auth._auth")
    def test_auth_user_role_reader(self, auth_mock):
        auth_mock.return_value = MagicMock(can_read=True, can_write=False,
                                           can_edit=False, can_admin=False)
        user_role = UserRole.reader
        permission_function = auth(user_role)
        self.assertEqual(permission_function, _can_read)

    @patch("app.auth._auth")
    def test_auth_user_role_writer(self, auth_mock):
        auth_mock.return_value = MagicMock(can_read=True, can_write=True,
                                           can_edit=False, can_admin=False)
        user_role = UserRole.writer
        permission_function = auth(user_role)
        self.assertEqual(permission_function, _can_write)

    @patch("app.auth._auth")
    def test_auth_user_role_editor(self, auth_mock):
        auth_mock.return_value = MagicMock(can_read=True, can_write=True,
                                           can_edit=True, can_admin=False)
        user_role = UserRole.editor
        permission_function = auth(user_role)
        self.assertEqual(permission_function, _can_edit)

    @patch("app.auth._auth")
    def test_auth_user_role_admin(self, auth_mock):
        auth_mock.return_value = MagicMock(can_read=True, can_write=True,
                                           can_edit=True, can_admin=True)
        user_role = UserRole.admin
        permission_function = auth(user_role)
        self.assertEqual(permission_function, _can_admin)

    @patch("app.auth._auth")
    async def test_can_read_success(self, auth_mock):
        auth_mock.return_value = MagicMock(can_read=True)
        session = AsyncMock()
        cache = AsyncMock()
        user = await _can_read(session=session, cache=cache,
                               header=MagicMock(credentials="token"))
        self.assertTrue(user.can_read)

    @patch("app.auth._auth")
    async def test_can_read_denied(self, auth_mock):
        auth_mock.return_value = MagicMock(can_read=False)
        session = AsyncMock()
        cache = AsyncMock()
        with self.assertRaises(E):
            await _can_read(session=session, cache=cache,
                            header=MagicMock(credentials="token"))

    @patch("app.auth._auth")
    async def test_can_write_success(self, auth_mock):
        auth_mock.return_value = MagicMock(can_write=True)
        session = AsyncMock()
        cache = AsyncMock()
        user = await _can_write(session=session, cache=cache,
                                header=MagicMock(credentials="token"))
        self.assertTrue(user.can_write)

    @patch("app.auth._auth")
    async def test_can_write_denied(self, auth_mock):
        auth_mock.return_value = MagicMock(can_write=False)
        session = AsyncMock()
        cache = AsyncMock()
        with self.assertRaises(E):
            await _can_write(session=session, cache=cache,
                             header=MagicMock(credentials="token"))

    @patch("app.auth._auth")
    async def test_can_edit_success(self, auth_mock):
        auth_mock.return_value = MagicMock(can_edit=True)
        session = AsyncMock()
        cache = AsyncMock()
        user = await _can_edit(session=session, cache=cache,
                               header=MagicMock(credentials="token"))
        self.assertTrue(user.can_edit)

    @patch("app.auth._auth")
    async def test_can_edit_denied(self, auth_mock):
        auth_mock.return_value = MagicMock(can_edit=False)
        session = AsyncMock()
        cache = AsyncMock()
        with self.assertRaises(E):
            await _can_edit(session=session, cache=cache,
                            header=MagicMock(credentials="token"))

    @patch("app.auth._auth")
    async def test_can_admin_success(self, auth_mock):
        auth_mock.return_value = MagicMock(can_admin=True)
        session = AsyncMock()
        cache = AsyncMock()
        user = await _can_admin(session=session, cache=cache,
                                header=MagicMock(credentials="token"))
        self.assertTrue(user.can_admin)

    @patch("app.auth._auth")
    async def test_can_admin_denied(self, auth_mock):
        auth_mock.return_value = MagicMock(can_admin=False)
        session = AsyncMock()
        cache = AsyncMock()
        with self.assertRaises(E):
            await _can_admin(session=session, cache=cache,
                             header=MagicMock(credentials="token"))

    @patch("app.auth.Repository")
    @patch("app.auth.jwt_decode")
    async def test_auth_token_correct(self, jwt_decode_mock, RepositoryMock):
        jwt_decode_mock.return_value = {"user_id": 1, "jti": "jti"}
        session = AsyncMock()
        cache = AsyncMock()
        user_mock = MagicMock(id=1, jti="jti", is_active=True,
                              suspended_date=0)

        user_repository = AsyncMock()
        user_repository.select.return_value = user_mock
        RepositoryMock.return_value = user_repository

        result = await _auth("token", session, cache)
        self.assertEqual(result, user_mock)

    @patch("app.auth.jwt_decode")
    async def test_auth_token_invalid(self, jwt_decode_mock):
        jwt_decode_mock.side_effect = PyJWTError()
        session = AsyncMock()
        cache = AsyncMock()
        with self.assertRaises(E):
            await _auth("token", session, cache)

    @patch("app.auth.jwt_decode")
    async def test_auth_token_expired(self, jwt_decode_mock):
        jwt_decode_mock.side_effect = ExpiredSignatureError()
        session = AsyncMock()
        cache = AsyncMock()
        with self.assertRaises(E):
            await _auth("expired_token", session, cache)

    async def test_auth_token_missing(self):
        session = AsyncMock()
        cache = AsyncMock()
        with self.assertRaises(E):
            await _auth(None, session, cache)


if __name__ == "__main__":
    unittest.main()
