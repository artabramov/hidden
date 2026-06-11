# tests/services/test_user_login.py
# SPDX-License-Identifier: GPL-3.0-only

import unittest
from unittest.mock import AsyncMock, MagicMock, patch

from app.constants import (
    AUTH_FAILED_PASSWORD_ATTEMPTS,
    AUTH_FAILED_SUSPEND_SECONDS,
)
from app.errors import ValueAuthenticationError
from app.events import Events as E
from app.models.user import User
from app.services.user_login import login_user


class TestLoginUser(unittest.IsolatedAsyncioTestCase):
    def _build_data(self, username="alice", password="secret"):
        data = MagicMock()
        data.username = username
        data.password = password
        return data

    def _build_user(self):
        user = MagicMock(spec=User)
        user.id = 42
        user.username = "alice"
        user.is_active = True
        user.password_hash = "stored-hash"
        user.failed_password_attempts = 0
        user.password_verified_at = None
        user.suspended_until = None
        user.mfa_session_uuid = None
        return user

    async def test_raises_when_user_not_found(self):
        session = AsyncMock()
        data = self._build_data()

        repository = AsyncMock()
        repository.select.return_value = None

        with (
            patch(
                "app.services.user_login.ORMRepository",
                return_value=repository
            ),
            patch(
                "app.services.user_login.hooks.emit",
                new=AsyncMock()
            ) as emit_mock,
        ):
            with self.assertRaises(ValueAuthenticationError):
                await login_user(session, data)

        repository.update.assert_not_awaited()
        repository.commit.assert_not_awaited()
        emit_mock.assert_not_awaited()

    async def test_raises_when_user_inactive(self):
        session = AsyncMock()
        data = self._build_data()
        user = self._build_user()
        user.is_active = False

        repository = AsyncMock()
        repository.select.return_value = user

        with (
            patch(
                "app.services.user_login.ORMRepository",
                return_value=repository
            ),
            patch(
                "app.services.user_login.hooks.emit",
                new=AsyncMock()
            ) as emit_mock,
        ):
            with self.assertRaises(ValueAuthenticationError):
                await login_user(session, data)

        repository.update.assert_not_awaited()
        repository.commit.assert_not_awaited()
        emit_mock.assert_not_awaited()

    async def test_raises_when_user_suspended(self):
        session = AsyncMock()
        data = self._build_data()
        user = self._build_user()

        now = 1_700_000_100
        user.suspended_until = now + 10

        repository = AsyncMock()
        repository.select.return_value = user

        with (
            patch(
                "app.services.user_login.ORMRepository",
                return_value=repository
            ),
            patch(
                "app.services.user_login.time.time",
                return_value=now
            ),
            patch(
                "app.services.user_login.hooks.emit",
                new=AsyncMock()
            ) as emit_mock,
        ):
            with self.assertRaises(ValueAuthenticationError):
                await login_user(session, data)

        repository.update.assert_not_awaited()
        repository.commit.assert_not_awaited()
        emit_mock.assert_not_awaited()

    async def test_successful_login_resets_counters_and_emits_hook(self):
        session = AsyncMock()
        data = self._build_data()
        user = self._build_user()
        user.failed_password_attempts = 3
        user.suspended_until = 123

        repository = AsyncMock()
        repository.select.return_value = user

        now = 1_700_000_100

        with (
            patch(
                "app.services.user_login.ORMRepository",
                return_value=repository
            ),
            patch(
                "app.services.user_login.time.time",
                return_value=now
            ),
            patch(
                "app.services.user_login.is_password_correct",
                return_value=True,
            ),
            patch(
                "app.services.user_login.generate_mfa_session_uuid",
                return_value="mfa-session-uuid-value",
            ),
            patch(
                "app.services.user_login.hooks.emit",
                new=AsyncMock()
            ) as emit_mock,
            patch(
                "app.services.user_login.write_audit",
                new=AsyncMock(),
            ) as write_audit_mock,
        ):
            result = await login_user(session, data)

        self.assertEqual(result, "mfa-session-uuid-value")
        self.assertEqual(user.mfa_session_uuid, "mfa-session-uuid-value")
        self.assertEqual(user.failed_password_attempts, 0)
        self.assertEqual(user.password_verified_at, now)
        self.assertIsNone(user.suspended_until)

        repository.update.assert_awaited_once_with(user)
        write_audit_mock.assert_awaited_once()
        repository.commit.assert_awaited_once()
        emit_mock.assert_awaited_once_with(
            E.USER_LOGIN_COMPLETED,
            session,
            user,
        )

    async def test_failed_login_increments_counter(self):
        session = AsyncMock()
        data = self._build_data()
        user = self._build_user()
        user.failed_password_attempts = 1

        repository = AsyncMock()
        repository.select.return_value = user

        now = 1_700_000_100

        with (
            patch(
                "app.services.user_login.ORMRepository",
                return_value=repository
            ),
            patch(
                "app.services.user_login.time.time",
                return_value=now
            ),
            patch(
                "app.services.user_login.is_password_correct",
                return_value=False,
            ),
            patch(
                "app.services.user_login.hooks.emit",
                new=AsyncMock()
            ) as emit_mock,
        ):
            with self.assertRaises(ValueAuthenticationError):
                await login_user(session, data)

        self.assertEqual(user.failed_password_attempts, 2)
        self.assertIsNone(user.password_verified_at)
        self.assertIsNone(user.suspended_until)

        repository.update.assert_awaited_once_with(user)
        repository.commit.assert_awaited_once()
        emit_mock.assert_not_awaited()

    async def test_failed_login_preserves_mfa_session_uuid(self):
        session = AsyncMock()
        data = self._build_data()
        user = self._build_user()
        user.mfa_session_uuid = "prior-mfa-session"

        repository = AsyncMock()
        repository.select.return_value = user

        now = 1_700_000_100

        with (
            patch(
                "app.services.user_login.ORMRepository",
                return_value=repository
            ),
            patch(
                "app.services.user_login.time.time",
                return_value=now
            ),
            patch(
                "app.services.user_login.is_password_correct",
                return_value=False,
            ),
            patch(
                "app.services.user_login.generate_mfa_session_uuid",
            ) as gen_uuid_mock,
            patch(
                "app.services.user_login.hooks.emit",
                new=AsyncMock()
            ) as emit_mock,
        ):
            with self.assertRaises(ValueAuthenticationError):
                await login_user(session, data)

        self.assertEqual(user.mfa_session_uuid, "prior-mfa-session")
        gen_uuid_mock.assert_not_called()
        emit_mock.assert_not_awaited()

    async def test_failed_login_triggers_suspension_on_limit(self):
        session = AsyncMock()
        data = self._build_data()
        user = self._build_user()

        now = 1_700_000_100
        user.failed_password_attempts = AUTH_FAILED_PASSWORD_ATTEMPTS - 1

        repository = AsyncMock()
        repository.select.return_value = user

        with (
            patch(
                "app.services.user_login.ORMRepository",
                return_value=repository
            ),
            patch(
                "app.services.user_login.time.time",
                return_value=now
            ),
            patch(
                "app.services.user_login.is_password_correct",
                return_value=False,
            ),
            patch(
                "app.services.user_login.hooks.emit",
                new=AsyncMock()
            ) as emit_mock,
        ):
            with self.assertRaises(ValueAuthenticationError):
                await login_user(session, data)

        self.assertEqual(user.failed_password_attempts, 0)
        self.assertEqual(
            user.suspended_until,
            now + AUTH_FAILED_SUSPEND_SECONDS,
        )
        self.assertIsNone(user.password_verified_at)

        repository.update.assert_awaited_once_with(user)
        repository.commit.assert_awaited_once()
        emit_mock.assert_not_awaited()
