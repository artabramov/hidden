import unittest
from unittest.mock import MagicMock, AsyncMock, patch
from app.auth import auth, _can_read, _can_write, _can_edit, _can_admin, _auth
from app.models.user_model import UserRole
from app.errors import E
from jwt.exceptions import ExpiredSignatureError, PyJWTError


class TestAuth(unittest.TestCase):

    @patch("app.auth._auth")
    def test_auth_reader(self, mock_auth):
        mock_auth.return_value = MagicMock(can_read=True, can_write=False,
                                           can_edit=False, can_admin=False)
        user_role = UserRole.reader
        permission_function = auth(user_role)
        self.assertEqual(permission_function, _can_read)

    @patch("app.auth._auth")
    def test_auth_writer(self, mock_auth):
        mock_auth.return_value = MagicMock(can_read=True, can_write=True,
                                           can_edit=False, can_admin=False)
        user_role = UserRole.writer
        permission_function = auth(user_role)
        self.assertEqual(permission_function, _can_write)

    @patch("app.auth._auth")
    def test_auth_editor(self, mock_auth):
        mock_auth.return_value = MagicMock(can_read=True, can_write=True,
                                           can_edit=True, can_admin=False)
        user_role = UserRole.editor
        permission_function = auth(user_role)
        self.assertEqual(permission_function, _can_edit)

    @patch("app.auth._auth")
    def test_auth_admin(self, mock_auth):
        mock_auth.return_value = MagicMock(can_read=True, can_write=True,
                                           can_edit=True, can_admin=True)
        user_role = UserRole.admin
        permission_function = auth(user_role)
        self.assertEqual(permission_function, _can_admin)

    @patch("app.auth._auth")
    async def test_can_read_success(self, mock_auth):
        mock_auth.return_value = MagicMock(can_read=True)
        session = AsyncMock()
        cache = AsyncMock()
        user = await _can_read(session=session, cache=cache,
                               header=MagicMock(credentials="valid_token"))
        self.assertTrue(user.can_read)

    @patch("app.auth._auth")
    async def test_can_read_permission_denied(self, mock_auth):
        mock_auth.return_value = MagicMock(can_read=False)
        session = AsyncMock()
        cache = AsyncMock()
        with self.assertRaises(E):
            await _can_read(session=session, cache=cache,
                            header=MagicMock(credentials="valid_token"))

    @patch("app.auth._auth")
    async def test_can_write_success(self, mock_auth):
        mock_auth.return_value = MagicMock(can_write=True)
        session = AsyncMock()
        cache = AsyncMock()
        user = await _can_write(session=session, cache=cache,
                                header=MagicMock(credentials="valid_token"))
        self.assertTrue(user.can_write)

    @patch("app.auth._auth")
    async def test_can_write_permission_denied(self, mock_auth):
        mock_auth.return_value = MagicMock(can_write=False)
        session = AsyncMock()
        cache = AsyncMock()
        with self.assertRaises(E):
            await _can_write(session=session, cache=cache,
                             header=MagicMock(credentials="valid_token"))

    @patch("app.auth._auth")
    async def test_can_edit_success(self, mock_auth):
        mock_auth.return_value = MagicMock(can_edit=True)
        session = AsyncMock()
        cache = AsyncMock()
        user = await _can_edit(session=session, cache=cache,
                               header=MagicMock(credentials="valid_token"))
        self.assertTrue(user.can_edit)

    @patch("app.auth._auth")
    async def test_can_edit_permission_denied(self, mock_auth):
        mock_auth.return_value = MagicMock(can_edit=False)
        session = AsyncMock()
        cache = AsyncMock()
        with self.assertRaises(E):
            await _can_edit(session=session, cache=cache,
                            header=MagicMock(credentials="valid_token"))

    @patch("app.auth._auth")
    async def test_can_admin_success(self, mock_auth):
        mock_auth.return_value = MagicMock(can_admin=True)
        session = AsyncMock()
        cache = AsyncMock()
        user = await _can_admin(session=session, cache=cache,
                                header=MagicMock(credentials="valid_token"))
        self.assertTrue(user.can_admin)

    @patch("app.auth._auth")
    async def test_can_admin_permission_denied(self, mock_auth):
        mock_auth.return_value = MagicMock(can_admin=False)
        session = AsyncMock()
        cache = AsyncMock()
        with self.assertRaises(E):
            await _can_admin(session=session, cache=cache,
                             header=MagicMock(credentials="valid_token"))

    @patch("app.auth.jwt_decode")
    async def test_auth_valid_token(self, mock_jwt_decode):
        mock_jwt_decode.return_value = {"user_id": 1, "jti": "valid_jti"}
        session = AsyncMock()
        cache = AsyncMock()
        user = MagicMock(id=1, jti="valid_jti", is_active=True,
                         suspended_date=0)
        session.select.return_value = user
        user = await _auth("valid_token", session, cache)
        self.assertEqual(user.id, 1)

    @patch("app.auth.jwt_decode")
    async def test_auth_invalid_token(self, mock_jwt_decode):
        mock_jwt_decode.side_effect = PyJWTError("Invalid token")
        session = AsyncMock()
        cache = AsyncMock()
        with self.assertRaises(E):
            await _auth("invalid_token", session, cache)

    @patch("app.auth.jwt_decode")
    async def test_auth_expired_token(self, mock_jwt_decode):
        mock_jwt_decode.side_effect = ExpiredSignatureError("Token expired")
        session = AsyncMock()
        cache = AsyncMock()
        with self.assertRaises(E):
            await _auth("expired_token", session, cache)

    @patch("app.auth.jwt_decode")
    async def test_auth_missing_token(self, mock_jwt_decode):
        session = AsyncMock()
        cache = AsyncMock()
        with self.assertRaises(E):
            await _auth(None, session, cache)


if __name__ == "__main__":
    unittest.main()
