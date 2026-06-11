# tests/dependencies/test_auth.py
# SPDX-License-Identifier: GPL-3.0-only

import unittest
from unittest.mock import AsyncMock, MagicMock, patch

import jwt
from fastapi import HTTPException


from tests.helpers import set_minimal_app_config_env


set_minimal_app_config_env()

import app.dependencies.auth as auth  # noqa: E402


def _bearer_creds(token: str = "tok", scheme: str = "Bearer") -> MagicMock:
    c = MagicMock()
    c.scheme = scheme
    c.credentials = token
    return c


def _mock_user(**overrides: object) -> MagicMock:
    u = MagicMock()
    u.current_jti_encrypted = "enc"
    u.is_active = True
    u.suspended_until = None
    u.can_read = True
    u.can_write = True
    u.can_edit = True
    u.can_admin = True
    for key, value in overrides.items():
        setattr(u, key, value)
    return u


class TestRequireAccess(unittest.IsolatedAsyncioTestCase):
    async def test_no_credentials_raises_401(self):
        session = MagicMock()
        dep = auth.require_access(auth.AccessLevel.READ)

        with patch("app.dependencies.auth.log.warning") as mock_warning:
            with self.assertRaises(HTTPException) as ctx:
                await dep(session=session, credentials=None)

        self.assertEqual(ctx.exception.status_code, 401)
        self.assertEqual(ctx.exception.detail, "Authentication required")
        mock_warning.assert_called_once_with(
            "event=%s",
            auth.E.AUTH_TOKEN_MISSING,
        )

    async def test_non_bearer_scheme_raises_401(self):
        session = MagicMock()
        dep = auth.require_access(auth.AccessLevel.READ)
        creds = _bearer_creds(scheme="Basic")

        with self.assertRaises(HTTPException) as ctx:
            await dep(session=session, credentials=creds)

        self.assertEqual(ctx.exception.status_code, 401)

    async def test_bearer_scheme_case_insensitive(self):
        session = MagicMock()
        user = _mock_user()
        creds = _bearer_creds(scheme="bearer")
        dep = auth.require_access(auth.AccessLevel.READ)

        with (
            patch(
                "app.dependencies.auth.decode_auth_token",
                return_value={"sub": "1", "jti": "jti-1"},
            ),
            patch(
                "app.dependencies.auth.decrypt_string",
                return_value="jti-1",
            ),
            patch("app.dependencies.auth.ORMRepository") as MockRepo,
        ):
            MockRepo.return_value.select = AsyncMock(return_value=user)
            out = await dep(session=session, credentials=creds)

        self.assertIs(out, user)

    async def test_invalid_jwt_raises_401(self):
        session = MagicMock()
        dep = auth.require_access(auth.AccessLevel.READ)
        creds = _bearer_creds()

        with (
            patch(
                "app.dependencies.auth.decode_auth_token",
                side_effect=jwt.InvalidTokenError(),
            ),
            patch("app.dependencies.auth.log.warning") as mock_warning,
        ):
            with self.assertRaises(HTTPException) as ctx:
                await dep(session=session, credentials=creds)

        self.assertEqual(ctx.exception.status_code, 401)
        self.assertEqual(
            ctx.exception.detail,
            "Invalid authentication token",
        )
        mock_warning.assert_called_once_with(
            "event=%s",
            auth.E.AUTH_TOKEN_INVALID,
        )

    async def test_payload_missing_sub_raises_401(self):
        session = MagicMock()
        dep = auth.require_access(auth.AccessLevel.READ)
        creds = _bearer_creds()

        with patch(
            "app.dependencies.auth.decode_auth_token",
            return_value={"jti": "x"},
        ):
            with self.assertRaises(HTTPException) as ctx:
                await dep(session=session, credentials=creds)

        self.assertEqual(ctx.exception.status_code, 401)

    async def test_payload_missing_jti_raises_401(self):
        session = MagicMock()
        dep = auth.require_access(auth.AccessLevel.READ)
        creds = _bearer_creds()

        with patch(
            "app.dependencies.auth.decode_auth_token",
            return_value={"sub": "1"},
        ):
            with self.assertRaises(HTTPException) as ctx:
                await dep(session=session, credentials=creds)

        self.assertEqual(ctx.exception.status_code, 401)

    async def test_user_not_found_raises_401(self):
        session = MagicMock()
        dep = auth.require_access(auth.AccessLevel.READ)
        creds = _bearer_creds()

        with (
            patch(
                "app.dependencies.auth.decode_auth_token",
                return_value={"sub": "99", "jti": "jti-1"},
            ),
            patch("app.dependencies.auth.ORMRepository") as MockRepo,
        ):
            MockRepo.return_value.select = AsyncMock(return_value=None)
            with self.assertRaises(HTTPException) as ctx:
                await dep(session=session, credentials=creds)

        self.assertEqual(ctx.exception.status_code, 401)

    async def test_current_jti_encrypted_none_raises_401(self):
        session = MagicMock()
        user = _mock_user(current_jti_encrypted=None)
        dep = auth.require_access(auth.AccessLevel.READ)
        creds = _bearer_creds()

        with (
            patch(
                "app.dependencies.auth.decode_auth_token",
                return_value={"sub": "1", "jti": "jti-1"},
            ),
            patch("app.dependencies.auth.ORMRepository") as MockRepo,
        ):
            MockRepo.return_value.select = AsyncMock(return_value=user)
            with self.assertRaises(HTTPException) as ctx:
                await dep(session=session, credentials=creds)

        self.assertEqual(ctx.exception.status_code, 401)

    async def test_jti_mismatch_raises_401(self):
        session = MagicMock()
        user = _mock_user()
        dep = auth.require_access(auth.AccessLevel.READ)
        creds = _bearer_creds()

        with (
            patch(
                "app.dependencies.auth.decode_auth_token",
                return_value={"sub": "1", "jti": "token-jti"},
            ),
            patch(
                "app.dependencies.auth.decrypt_string",
                return_value="other-jti",
            ),
            patch("app.dependencies.auth.ORMRepository") as MockRepo,
        ):
            MockRepo.return_value.select = AsyncMock(return_value=user)
            with self.assertRaises(HTTPException) as ctx:
                await dep(session=session, credentials=creds)

        self.assertEqual(ctx.exception.status_code, 401)

    async def test_inactive_user_raises_403(self):
        session = MagicMock()
        user = _mock_user(is_active=False)
        dep = auth.require_access(auth.AccessLevel.READ)
        creds = _bearer_creds()

        with (
            patch(
                "app.dependencies.auth.decode_auth_token",
                return_value={"sub": "1", "jti": "jti-1"},
            ),
            patch(
                "app.dependencies.auth.decrypt_string",
                return_value="jti-1",
            ),
            patch("app.dependencies.auth.ORMRepository") as MockRepo,
        ):
            MockRepo.return_value.select = AsyncMock(return_value=user)
            with self.assertRaises(HTTPException) as ctx:
                await dep(session=session, credentials=creds)

        self.assertEqual(ctx.exception.status_code, 403)
        self.assertEqual(ctx.exception.detail, "Access denied")

    async def test_suspended_user_raises_403(self):
        session = MagicMock()
        user = _mock_user()
        dep = auth.require_access(auth.AccessLevel.READ)
        creds = _bearer_creds()

        with (
            patch(
                "app.dependencies.auth.decode_auth_token",
                return_value={"sub": "1", "jti": "jti-1"},
            ),
            patch(
                "app.dependencies.auth.decrypt_string",
                return_value="jti-1",
            ),
            patch("app.dependencies.auth.ORMRepository") as MockRepo,
            patch("app.dependencies.auth.time.time", return_value=1000),
        ):
            user.suspended_until = 2000
            MockRepo.return_value.select = AsyncMock(return_value=user)
            with self.assertRaises(HTTPException) as ctx:
                await dep(session=session, credentials=creds)

        self.assertEqual(ctx.exception.status_code, 403)

    async def test_suspended_until_none_or_past_allows(self):
        session = MagicMock()
        user = _mock_user()
        dep = auth.require_access(auth.AccessLevel.READ)
        creds = _bearer_creds()

        with (
            patch(
                "app.dependencies.auth.decode_auth_token",
                return_value={"sub": "1", "jti": "jti-1"},
            ),
            patch(
                "app.dependencies.auth.decrypt_string",
                return_value="jti-1",
            ),
            patch("app.dependencies.auth.ORMRepository") as MockRepo,
            patch("app.dependencies.auth.time.time", return_value=5000),
        ):
            user.suspended_until = 1000
            MockRepo.return_value.select = AsyncMock(return_value=user)
            out = await dep(session=session, credentials=creds)

        self.assertIs(out, user)

    async def test_missing_access_level_raises_403(self):
        session = MagicMock()
        user = _mock_user(can_admin=False)
        dep = auth.require_access(auth.AccessLevel.ADMIN)
        creds = _bearer_creds()

        with (
            patch(
                "app.dependencies.auth.decode_auth_token",
                return_value={"sub": "1", "jti": "jti-1"},
            ),
            patch(
                "app.dependencies.auth.decrypt_string",
                return_value="jti-1",
            ),
            patch("app.dependencies.auth.ORMRepository") as MockRepo,
        ):
            MockRepo.return_value.select = AsyncMock(return_value=user)
            with self.assertRaises(HTTPException) as ctx:
                await dep(session=session, credentials=creds)

        self.assertEqual(ctx.exception.status_code, 403)

    async def test_success_returns_user(self):
        session = MagicMock()
        user = _mock_user()
        dep = auth.require_access(auth.AccessLevel.WRITE)
        creds = _bearer_creds()

        with (
            patch(
                "app.dependencies.auth.decode_auth_token",
                return_value={"sub": "42", "jti": "jti-1"},
            ),
            patch(
                "app.dependencies.auth.decrypt_string",
                return_value="jti-1",
            ),
            patch("app.dependencies.auth.ORMRepository") as MockRepo,
            patch("app.dependencies.auth.log.info") as mock_info,
        ):
            mock_select = AsyncMock(return_value=user)
            MockRepo.return_value.select = mock_select
            out = await dep(session=session, credentials=creds)

        self.assertIs(out, user)
        mock_select.assert_awaited_once()
        call_kw = mock_select.await_args.kwargs
        self.assertEqual(call_kw.get("id"), 42)
        mock_info.assert_any_call(
            "event=%s user_id=%s",
            auth.E.AUTH_COMPLETED,
            42,
        )

    async def test_payload_non_numeric_sub_raises_401(self):
        session = MagicMock()
        dep = auth.require_access(auth.AccessLevel.READ)
        creds = _bearer_creds()

        with patch(
            "app.dependencies.auth.decode_auth_token",
            return_value={"sub": "abc", "jti": "jti-1"},
        ):
            with self.assertRaises(HTTPException) as ctx:
                await dep(session=session, credentials=creds)

        self.assertEqual(ctx.exception.status_code, 401)
        self.assertEqual(
            ctx.exception.detail,
            "Invalid authentication token",
        )

    async def test_payload_sub_with_invalid_type_raises_401(self):
        session = MagicMock()
        dep = auth.require_access(auth.AccessLevel.READ)
        creds = _bearer_creds()

        with patch(
            "app.dependencies.auth.decode_auth_token",
            return_value={"sub": [], "jti": "jti-1"},
        ):
            with self.assertRaises(HTTPException) as ctx:
                await dep(session=session, credentials=creds)

        self.assertEqual(ctx.exception.status_code, 401)
        self.assertEqual(
            ctx.exception.detail,
            "Invalid authentication token",
        )

    async def test_decrypt_string_failure_raises_401(self):
        session = MagicMock()
        user = _mock_user()
        dep = auth.require_access(auth.AccessLevel.READ)
        creds = _bearer_creds()

        with (
            patch(
                "app.dependencies.auth.decode_auth_token",
                return_value={"sub": "1", "jti": "jti-1"},
            ),
            patch(
                "app.dependencies.auth.decrypt_string",
                side_effect=ValueError("broken ciphertext"),
            ),
            patch("app.dependencies.auth.ORMRepository") as MockRepo,
        ):
            MockRepo.return_value.select = AsyncMock(return_value=user)

            with self.assertRaises(HTTPException) as ctx:
                await dep(session=session, credentials=creds)

        self.assertEqual(ctx.exception.status_code, 401)
        self.assertEqual(
            ctx.exception.detail,
            "Invalid authentication token",
        )

    async def test_decrypt_string_failure_unexpected_error_raises_401(self):
        session = MagicMock()
        user = _mock_user()
        dep = auth.require_access(auth.AccessLevel.READ)
        creds = _bearer_creds()

        with (
            patch(
                "app.dependencies.auth.decode_auth_token",
                return_value={"sub": "1", "jti": "jti-1"},
            ),
            patch(
                "app.dependencies.auth.decrypt_string",
                side_effect=RuntimeError("unexpected decrypt error"),
            ),
            patch("app.dependencies.auth.ORMRepository") as MockRepo,
        ):
            MockRepo.return_value.select = AsyncMock(return_value=user)

            with self.assertRaises(HTTPException) as ctx:
                await dep(session=session, credentials=creds)

        self.assertEqual(ctx.exception.status_code, 401)
        self.assertEqual(
            ctx.exception.detail,
            "Invalid authentication token",
        )

    async def test_empty_current_jti_encrypted_raises_401(self):
        session = MagicMock()
        user = _mock_user(current_jti_encrypted="")
        dep = auth.require_access(auth.AccessLevel.READ)
        creds = _bearer_creds()

        with (
            patch(
                "app.dependencies.auth.decode_auth_token",
                return_value={"sub": "1", "jti": "jti-1"},
            ),
            patch("app.dependencies.auth.ORMRepository") as MockRepo,
        ):
            MockRepo.return_value.select = AsyncMock(return_value=user)

            with self.assertRaises(HTTPException) as ctx:
                await dep(session=session, credentials=creds)

        self.assertEqual(ctx.exception.status_code, 401)
        self.assertEqual(
            ctx.exception.detail,
            "Invalid authentication token",
        )

    async def test_decrypt_string_not_called_when_jti_encrypted_missing(self):
        session = MagicMock()
        user = _mock_user(current_jti_encrypted=None)
        dep = auth.require_access(auth.AccessLevel.READ)
        creds = _bearer_creds()

        with (
            patch(
                "app.dependencies.auth.decode_auth_token",
                return_value={"sub": "1", "jti": "jti-1"},
            ),
            patch("app.dependencies.auth.decrypt_string") as mock_decrypt,
            patch("app.dependencies.auth.ORMRepository") as MockRepo,
        ):
            MockRepo.return_value.select = AsyncMock(return_value=user)

            with self.assertRaises(HTTPException) as ctx:
                await dep(session=session, credentials=creds)

        self.assertEqual(ctx.exception.status_code, 401)
        self.assertEqual(
            ctx.exception.detail,
            "Invalid authentication token",
        )
        mock_decrypt.assert_not_called()
