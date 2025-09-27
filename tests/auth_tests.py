import time
import unittest
from unittest.mock import MagicMock, AsyncMock, patch
from jwt.exceptions import ExpiredSignatureError, PyJWTError
from app.auth import auth, _can_read, _can_write, _can_edit, _can_admin, _auth
from app.models.user import UserRole
from app.error import E


class TestAuth(unittest.IsolatedAsyncioTestCase):

    @patch("app.auth._auth")
    async def test_header_wrong_scheme_401(self, _auth_mock):
        _auth_mock.return_value = MagicMock(can_read=True)
        session = AsyncMock()
        cache = AsyncMock()
        request = MagicMock()
        request.state = MagicMock()
        request.state.log = MagicMock()

        header = MagicMock(scheme="Basic", credentials="token")
        with self.assertRaises(E):
            await _can_read(request=request, session=session, cache=cache,
                            header=header)

    @patch("app.auth._auth")
    async def test_header_empty_credentials_401(self, _auth_mock):
        _auth_mock.return_value = MagicMock(can_read=True)
        session = AsyncMock()
        cache = AsyncMock()
        request = MagicMock()
        request.state = MagicMock()
        request.state.log = MagicMock()

        header = MagicMock(scheme="Bearer", credentials=None)
        with self.assertRaises(E):
            await _can_read(request=request, session=session, cache=cache,
                            header=header)

    @patch("app.auth.decode_jwt")
    async def test_payload_non_int_user_id_401(self, decode_jwt_mock):
        decode_jwt_mock.return_value = {"user_id": "1", "jti": "jti"}
        session = AsyncMock()
        cache = AsyncMock()

        request = MagicMock()
        request.app = MagicMock()
        request.app.state = MagicMock()
        request.app.state.config = MagicMock(
            JWT_SECRET="s", JWT_ALGORITHMS=["HS256"])
        request.state = MagicMock()
        request.state.secret_key = "k"

        with self.assertRaises(E):
            await _auth(request, "token", session, cache)

    @patch("app.auth.decode_jwt")
    async def test_payload_missing_jti_401(self, decode_jwt_mock):
        decode_jwt_mock.return_value = {"user_id": 1, "jti": None}
        session = AsyncMock()
        cache = AsyncMock()

        request = MagicMock()
        request.app = MagicMock()
        request.app.state = MagicMock()
        request.app.state.config = MagicMock(
            JWT_SECRET="s", JWT_ALGORITHMS=["HS256"])
        request.state = MagicMock()
        request.state.secret_key = "k"

        with self.assertRaises(E):
            await _auth(request, "token", session, cache)

    @patch("app.auth.Repository")
    @patch("app.auth.decode_jwt")
    async def test_user_not_found_403(self, decode_jwt_mock, RepositoryMock):
        decode_jwt_mock.return_value = {"user_id": 1, "jti": "jti"}
        session = AsyncMock()
        cache = AsyncMock()

        user_repository = AsyncMock()
        user_repository.select.return_value = None
        RepositoryMock.return_value = user_repository

        request = MagicMock()
        request.app = MagicMock()
        request.app.state = MagicMock()
        request.app.state.config = MagicMock(
            JWT_SECRET="s", JWT_ALGORITHMS=["HS256"])
        request.state = MagicMock()
        request.state.secret_key = "k"

        with self.assertRaises(E):
            await _auth(request, "token", session, cache)

    @patch("app.auth.Repository")
    @patch("app.auth.decode_jwt")
    async def test_user_inactive_403(self, decode_jwt_mock, RepositoryMock):
        decode_jwt_mock.return_value = {"user_id": 1, "jti": "jti"}
        session = AsyncMock()
        cache = AsyncMock()

        user_mock = MagicMock(active=False, suspended_until_date=0,
                              jti_encrypted="enc")
        user_repository = AsyncMock()
        user_repository.select.return_value = user_mock
        RepositoryMock.return_value = user_repository

        request = MagicMock()
        request.app = MagicMock()
        request.app.state = MagicMock()
        request.app.state.config = MagicMock(
            JWT_SECRET="s", JWT_ALGORITHMS=["HS256"])
        request.state = MagicMock()
        request.state.secret_key = "k"

        with self.assertRaises(E):
            await _auth(request, "token", session, cache)

    @patch("app.auth.Repository")
    @patch("app.auth.decode_jwt")
    async def test_user_suspended_403(self, decode_jwt_mock, RepositoryMock):
        decode_jwt_mock.return_value = {"user_id": 1, "jti": "jti"}
        session = AsyncMock()
        cache = AsyncMock()

        future = int(time.time()) + 3600
        user_mock = MagicMock(active=True, suspended_until_date=future,
                              jti_encrypted="enc")
        user_repository = AsyncMock()
        user_repository.select.return_value = user_mock
        RepositoryMock.return_value = user_repository

        request = MagicMock()
        request.app = MagicMock()
        request.app.state = MagicMock()
        request.app.state.config = MagicMock(
            JWT_SECRET="s", JWT_ALGORITHMS=["HS256"])
        request.state = MagicMock()
        request.state.secret_key = "k"

        with self.assertRaises(E):
            await _auth(request, "token", session, cache)

    @patch("app.auth.EncryptionManager")
    @patch("app.auth.Repository")
    @patch("app.auth.decode_jwt")
    async def test_jti_mismatch_403(self, decode_jwt_mock, RepositoryMock,
                                    EncryptionManagerMock):
        decode_jwt_mock.return_value = {"user_id": 1, "jti": "token_jti"}
        session = AsyncMock()
        cache = AsyncMock()

        user_mock = MagicMock(active=True, suspended_until_date=0,
                              jti_encrypted="enc")
        user_repository = AsyncMock()
        user_repository.select.return_value = user_mock
        RepositoryMock.return_value = user_repository

        enc = EncryptionManagerMock.return_value
        enc.decrypt_str.return_value = "db_jti_differs"

        request = MagicMock()
        request.app = MagicMock()
        request.app.state = MagicMock()
        request.app.state.config = MagicMock(
            JWT_SECRET="s", JWT_ALGORITHMS=["HS256"])
        request.state = MagicMock()
        request.state.secret_key = "k"

        with self.assertRaises(E):
            await _auth(request, "token", session, cache)

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
        request = MagicMock()
        request.state = MagicMock()
        request.state.log = MagicMock()

        header = MagicMock(scheme="Bearer", credentials="token")
        user = await _can_read(request=request, session=session, cache=cache,
                               header=header)
        self.assertTrue(user.can_read)

    @patch("app.auth._auth")
    async def test_can_read_denied(self, auth_mock):
        auth_mock.return_value = MagicMock(can_read=False)
        session = AsyncMock()
        cache = AsyncMock()
        request = MagicMock()
        request.state = MagicMock()
        request.state.log = MagicMock()

        header = MagicMock(scheme="Bearer", credentials="token")
        with self.assertRaises(E):
            await _can_read(request=request, session=session, cache=cache,
                            header=header)

    @patch("app.auth._auth")
    async def test_can_write_success(self, auth_mock):
        auth_mock.return_value = MagicMock(can_write=True)
        session = AsyncMock()
        cache = AsyncMock()
        request = MagicMock()
        request.state = MagicMock()
        request.state.log = MagicMock()

        header = MagicMock(scheme="Bearer", credentials="token")
        user = await _can_write(request=request, session=session, cache=cache,
                                header=header)
        self.assertTrue(user.can_write)

    @patch("app.auth._auth")
    async def test_can_write_denied(self, auth_mock):
        auth_mock.return_value = MagicMock(can_write=False)
        session = AsyncMock()
        cache = AsyncMock()
        request = MagicMock()
        request.state = MagicMock()
        request.state.log = MagicMock()

        header = MagicMock(scheme="Bearer", credentials="token")
        with self.assertRaises(E):
            await _can_write(request=request, session=session, cache=cache,
                             header=header)

    @patch("app.auth._auth")
    async def test_can_edit_success(self, auth_mock):
        auth_mock.return_value = MagicMock(can_edit=True)
        session = AsyncMock()
        cache = AsyncMock()
        request = MagicMock()
        request.state = MagicMock()
        request.state.log = MagicMock()

        header = MagicMock(scheme="Bearer", credentials="token")
        user = await _can_edit(request=request, session=session, cache=cache,
                               header=header)
        self.assertTrue(user.can_edit)

    @patch("app.auth._auth")
    async def test_can_edit_denied(self, auth_mock):
        auth_mock.return_value = MagicMock(can_edit=False)
        session = AsyncMock()
        cache = AsyncMock()
        request = MagicMock()
        request.state = MagicMock()
        request.state.log = MagicMock()

        header = MagicMock(scheme="Bearer", credentials="token")
        with self.assertRaises(E):
            await _can_edit(request=request, session=session, cache=cache,
                            header=header)

    @patch("app.auth._auth")
    async def test_can_admin_success(self, auth_mock):
        auth_mock.return_value = MagicMock(can_admin=True)
        session = AsyncMock()
        cache = AsyncMock()
        request = MagicMock()
        request.state = MagicMock()
        request.state.log = MagicMock()

        header = MagicMock(scheme="Bearer", credentials="token")
        user = await _can_admin(request=request, session=session, cache=cache,
                                header=header)
        self.assertTrue(user.can_admin)

    @patch("app.auth._auth")
    async def test_can_admin_denied(self, auth_mock):
        auth_mock.return_value = MagicMock(can_admin=False)
        session = AsyncMock()
        cache = AsyncMock()
        request = MagicMock()
        request.state = MagicMock()
        request.state.log = MagicMock()

        header = MagicMock(scheme="Bearer", credentials="token")
        with self.assertRaises(E):
            await _can_admin(request=request, session=session, cache=cache,
                             header=header)

    @patch("app.auth.EncryptionManager")
    @patch("app.auth.Repository")
    @patch("app.auth.decode_jwt")
    async def test_auth_token_correct(self, decode_jwt_mock, RepositoryMock,
                                      EncryptionManagerMock):
        # Arrange
        decode_jwt_mock.return_value = {"user_id": 1, "jti": "jti"}

        session = AsyncMock()
        cache = AsyncMock()

        user_mock = MagicMock(
            id=1,
            active=True,
            suspended_until_date=0,
            jti_encrypted="enc"
        )

        user_repository = AsyncMock()
        user_repository.select.return_value = user_mock
        RepositoryMock.return_value = user_repository

        enc = EncryptionManagerMock.return_value
        enc.decrypt_str.return_value = "jti"

        config = MagicMock(JWT_SECRET="secret", JWT_ALGORITHMS=["HS256"])
        request = MagicMock()
        request.app = MagicMock()
        request.app.state = MagicMock()
        request.app.state.config = config
        request.state = MagicMock()
        request.state.secret_key = "k"

        result = await _auth(request, "token", session, cache)
        self.assertEqual(result, user_mock)
        enc.decrypt_str.assert_called_once_with("enc")

    @patch("app.auth.decode_jwt")
    async def test_auth_token_invalid(self, decode_jwt_mock):
        decode_jwt_mock.side_effect = PyJWTError()
        session = AsyncMock()
        cache = AsyncMock()

        config = MagicMock(JWT_SECRET="secret", JWT_ALGORITHMS=["HS256"])
        request = MagicMock()
        request.app = MagicMock()
        request.app.state = MagicMock()
        request.app.state.config = config
        request.state = MagicMock()
        request.state.secret_key = "k"

        with self.assertRaises(E):
            await _auth(request, "token", session, cache)

    @patch("app.auth.decode_jwt")
    async def test_auth_token_expired(self, decode_jwt_mock):
        decode_jwt_mock.side_effect = ExpiredSignatureError()
        session = AsyncMock()
        cache = AsyncMock()

        config = MagicMock(JWT_SECRET="secret", JWT_ALGORITHMS=["HS256"])
        request = MagicMock()
        request.app = MagicMock()
        request.app.state = MagicMock()
        request.app.state.config = config
        request.state = MagicMock()
        request.state.secret_key = "k"

        with self.assertRaises(E):
            await _auth(request, "expired_token", session, cache)

    async def test_auth_token_missing(self):
        session = AsyncMock()
        cache = AsyncMock()
        request = MagicMock()
        request.state = MagicMock()
        request.state.log = MagicMock()

        with self.assertRaises(E):
            await _can_read(request=request, session=session, cache=cache,
                            header=None)
