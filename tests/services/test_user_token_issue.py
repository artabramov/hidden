# tests/services/test_user_token_issue.py
# SPDX-License-Identifier: SSPL-1.0

import unittest
from unittest.mock import AsyncMock, MagicMock, patch

from app.errors import ResourceConflictError, ValueAuthenticationError
from app.events import Events as E
from app.models.user import User
from app.services.user_token_issue import issue_token
from app.constants import (
    AUTH_FAILED_TOTP_ATTEMPTS,
    AUTH_FAILED_SUSPEND_SECONDS,
    AUTH_PASSWORD_VERIFIED_TTL_SECONDS,
)


class TestIssueToken(unittest.IsolatedAsyncioTestCase):
    _DEFAULT_MFA_SESSION_UUID = "mfa-session-" + "x" * 15

    def _build_data(
        self,
        mfa_session_uuid=None,
        totp="123456",
        disable_exp=False,
    ):
        data = MagicMock()
        data.mfa_session_uuid = (
            mfa_session_uuid
            if mfa_session_uuid is not None
            else self._DEFAULT_MFA_SESSION_UUID
        )
        data.totp = totp
        data.disable_exp = disable_exp
        return data

    def _build_user(self):
        user = MagicMock(spec=User)
        user.id = 42
        user.username = "alice"
        user.is_active = True
        user.suspended_until = None
        user.password_verified_at = 1_700_000_000
        user.mfa_session_uuid = "prior-mfa-session-" + "y" * 10
        user.totp_secret_encrypted = "encrypted-secret"
        user.failed_totp_attempts = 0
        user.current_jti_encrypted = "old-jti"
        user.last_authenticated_at = None
        return user

    async def test_raises_authentication_error_when_user_not_found(self):
        session = AsyncMock()
        data = self._build_data()

        repository = AsyncMock()
        repository.select.return_value = None

        with patch(
            "app.services.user_token_issue.ORMRepository",
            return_value=repository,
        ):
            with self.assertRaises(ValueAuthenticationError) as cm:
                await issue_token(session, data)

        repository.select.assert_awaited_once_with(
            User,
            mfa_session_uuid=self._DEFAULT_MFA_SESSION_UUID,
        )
        repository.update.assert_not_awaited()
        repository.commit.assert_not_awaited()

        error = cm.exception
        self.assertEqual(error.input_value, "123456")
        self.assertEqual(error.loc, ("body", "totp"))

    async def test_raises_authentication_error_when_user_is_inactive(self):
        session = AsyncMock()
        data = self._build_data()
        user = self._build_user()
        user.is_active = False

        repository = AsyncMock()
        repository.select.return_value = user

        with patch(
            "app.services.user_token_issue.ORMRepository",
            return_value=repository,
        ):
            with self.assertRaises(ValueAuthenticationError) as cm:
                await issue_token(session, data)

        repository.select.assert_awaited_once_with(
            User,
            mfa_session_uuid=self._DEFAULT_MFA_SESSION_UUID,
        )
        repository.update.assert_not_awaited()
        repository.commit.assert_not_awaited()

        error = cm.exception
        self.assertEqual(error.input_value, "123456")
        self.assertEqual(error.loc, ("body", "totp"))

    async def test_raises_authentication_error_when_user_is_suspended(self):
        session = AsyncMock()
        data = self._build_data()
        user = self._build_user()

        now = 1_700_000_100
        user.suspended_until = now + 10

        repository = AsyncMock()
        repository.select.return_value = user

        with (
            patch(
                "app.services.user_token_issue.ORMRepository",
                return_value=repository,
            ),
            patch(
                "app.services.user_token_issue.time.time",
                return_value=now,
            ),
        ):
            with self.assertRaises(ValueAuthenticationError) as cm:
                await issue_token(session, data)

        repository.select.assert_awaited_once_with(
            User,
            mfa_session_uuid=self._DEFAULT_MFA_SESSION_UUID,
        )
        repository.update.assert_not_awaited()
        repository.commit.assert_not_awaited()

        error = cm.exception
        self.assertEqual(error.input_value, "123456")
        self.assertEqual(error.loc, ("body", "totp"))

    async def test_raises_resource_conflict_when_password_not_verified(self):
        session = AsyncMock()
        data = self._build_data()
        user = self._build_user()
        user.password_verified_at = None

        repository = AsyncMock()
        repository.select.return_value = user

        with (
            patch(
                "app.services.user_token_issue.ORMRepository",
                return_value=repository,
            ),
            patch(
                "app.services.user_token_issue.time.time",
                return_value=1_700_000_100,
            ),
        ):
            with self.assertRaises(ResourceConflictError):
                await issue_token(session, data)

        repository.select.assert_awaited_once_with(
            User,
            mfa_session_uuid=self._DEFAULT_MFA_SESSION_UUID,
        )
        self.assertIsNone(user.mfa_session_uuid)
        self.assertIsNone(user.password_verified_at)
        repository.update.assert_awaited_once_with(user)
        repository.commit.assert_awaited_once_with()

    async def test_raises_resource_conflict_when_password_expired(self):
        session = AsyncMock()
        data = self._build_data()
        user = self._build_user()

        now = 1_700_000_100
        user.password_verified_at = (
            now - AUTH_PASSWORD_VERIFIED_TTL_SECONDS - 1
        )

        repository = AsyncMock()
        repository.select.return_value = user

        with (
            patch(
                "app.services.user_token_issue.ORMRepository",
                return_value=repository,
            ),
            patch(
                "app.services.user_token_issue.time.time",
                return_value=now,
            ),
        ):
            with self.assertRaises(ResourceConflictError):
                await issue_token(session, data)

        repository.select.assert_awaited_once_with(
            User,
            mfa_session_uuid=self._DEFAULT_MFA_SESSION_UUID,
        )
        self.assertIsNone(user.mfa_session_uuid)
        self.assertIsNone(user.password_verified_at)
        repository.update.assert_awaited_once_with(user)
        repository.commit.assert_awaited_once_with()

    async def test_succeeds_when_password_verified_ttl_boundary_exact(self):
        """
        Expiry uses `verified_at + TTL < now`; at `now == verified_at + TTL`
        the window is still inclusive on the last second.
        """
        session = AsyncMock()
        data = self._build_data()
        user = self._build_user()
        now = 1_700_000_100
        user.password_verified_at = now - AUTH_PASSWORD_VERIFIED_TTL_SECONDS

        repository = AsyncMock()
        repository.select.return_value = user

        with (
            patch(
                "app.services.user_token_issue.ORMRepository",
                return_value=repository,
            ),
            patch(
                "app.services.user_token_issue.time.time",
                return_value=now,
            ),
            patch(
                "app.services.user_token_issue.decrypt_string",
                return_value="plain-secret",
            ),
            patch(
                "app.services.user_token_issue.is_totp_correct",
                return_value=True,
            ),
            patch(
                "app.services.user_token_issue.generate_jti",
                return_value="new-jti",
            ),
            patch(
                "app.services.user_token_issue.create_auth_token",
                return_value="auth-token",
            ),
            patch(
                "app.services.user_token_issue.encrypt_string",
                return_value="enc-jti",
            ),
            patch(
                "app.services.user_token_issue.hooks.emit",
                new=AsyncMock(),
            ),
            patch(
                "app.services.user_token_issue.write_audit",
                new=AsyncMock(),
            ),
        ):
            uid, token = await issue_token(session, data)

        self.assertEqual(uid, 42)
        self.assertEqual(token, "auth-token")

    async def test_increments_failed_totp_attempts_raises_authentication_error(
        self,
    ):
        session = AsyncMock()
        data = self._build_data()
        user = self._build_user()
        user.failed_totp_attempts = 1

        repository = AsyncMock()
        repository.select.return_value = user

        with (
            patch(
                "app.services.user_token_issue.ORMRepository",
                return_value=repository,
            ),
            patch(
                "app.services.user_token_issue.time.time",
                return_value=1_700_000_100,
            ),
            patch(
                "app.services.user_token_issue.decrypt_string",
                return_value="plain-secret",
            ) as decrypt_mock,
            patch(
                "app.services.user_token_issue.is_totp_correct",
                return_value=False,
            ) as totp_mock,
            patch(
                "app.services.user_token_issue.hooks.emit",
                new=AsyncMock(),
            ) as emit_mock,
        ):
            with self.assertRaises(ValueAuthenticationError) as cm:
                await issue_token(session, data)

        repository.select.assert_awaited_once_with(
            User,
            mfa_session_uuid=self._DEFAULT_MFA_SESSION_UUID,
        )
        decrypt_mock.assert_called_once_with("encrypted-secret")
        totp_mock.assert_called_once_with("plain-secret", "123456")

        self.assertEqual(user.failed_totp_attempts, 2)
        self.assertEqual(user.password_verified_at, 1_700_000_000)
        self.assertIsNone(user.suspended_until)

        repository.update.assert_awaited_once_with(user)
        repository.commit.assert_awaited_once_with()
        emit_mock.assert_not_awaited()

        error = cm.exception
        self.assertEqual(error.input_value, "123456")
        self.assertEqual(error.loc, ("body", "totp"))

    async def test_resets_failed_attempts_suspends_user_on_totp_limit(self):
        session = AsyncMock()
        data = self._build_data()
        user = self._build_user()

        now = 1_700_000_100
        user.failed_totp_attempts = AUTH_FAILED_TOTP_ATTEMPTS - 1

        repository = AsyncMock()
        repository.select.return_value = user

        with (
            patch(
                "app.services.user_token_issue.ORMRepository",
                return_value=repository,
            ),
            patch(
                "app.services.user_token_issue.time.time",
                return_value=now,
            ),
            patch(
                "app.services.user_token_issue.decrypt_string",
                return_value="plain-secret",
            ) as decrypt_mock,
            patch(
                "app.services.user_token_issue.is_totp_correct",
                return_value=False,
            ) as totp_mock,
            patch(
                "app.services.user_token_issue.hooks.emit",
                new=AsyncMock(),
            ) as emit_mock,
        ):
            with self.assertRaises(ValueAuthenticationError) as cm:
                await issue_token(session, data)

        repository.select.assert_awaited_once_with(
            User,
            mfa_session_uuid=self._DEFAULT_MFA_SESSION_UUID,
        )
        decrypt_mock.assert_called_once_with("encrypted-secret")
        totp_mock.assert_called_once_with("plain-secret", "123456")

        self.assertEqual(user.failed_totp_attempts, 0)
        self.assertIsNone(user.password_verified_at)
        self.assertIsNone(user.mfa_session_uuid)
        self.assertEqual(
            user.suspended_until,
            now + AUTH_FAILED_SUSPEND_SECONDS,
        )

        repository.update.assert_awaited_once_with(user)
        repository.commit.assert_awaited_once_with()
        emit_mock.assert_not_awaited()

        error = cm.exception
        self.assertEqual(error.input_value, "123456")
        self.assertEqual(error.loc, ("body", "totp"))

    async def test_issues_token_and_updates_user_auth_state(self):
        session = AsyncMock()
        data = self._build_data()
        user = self._build_user()
        user.failed_totp_attempts = 3

        repository = AsyncMock()
        repository.select.return_value = user

        now = 1_700_000_100

        with (
            patch(
                "app.services.user_token_issue.ORMRepository",
                return_value=repository,
            ),
            patch(
                "app.services.user_token_issue.time.time",
                return_value=now,
            ),
            patch(
                "app.services.user_token_issue.decrypt_string",
                return_value="plain-secret",
            ) as decrypt_mock,
            patch(
                "app.services.user_token_issue.is_totp_correct",
                return_value=True,
            ) as totp_mock,
            patch(
                "app.services.user_token_issue.generate_jti",
                return_value="new-jti",
            ) as generate_jti_mock,
            patch(
                "app.services.user_token_issue.create_auth_token",
                return_value="auth-token",
            ) as create_token_mock,
            patch(
                "app.services.user_token_issue.encrypt_string",
                return_value="encrypted-new-jti",
            ) as encrypt_mock,
            patch(
                "app.services.user_token_issue.hooks.emit",
                new=AsyncMock(),
            ) as emit_mock,
            patch(
                "app.services.user_token_issue.write_audit",
                new=AsyncMock(),
            ) as write_audit_mock,
        ):
            user_id, auth_token = await issue_token(session, data)

        repository.select.assert_awaited_once_with(
            User,
            mfa_session_uuid=self._DEFAULT_MFA_SESSION_UUID,
        )
        decrypt_mock.assert_called_once_with("encrypted-secret")
        totp_mock.assert_called_once_with("plain-secret", "123456")
        generate_jti_mock.assert_called_once_with()
        create_token_mock.assert_called_once_with(
            42,
            "new-jti",
            disable_exp=False,
        )
        encrypt_mock.assert_called_once_with("new-jti")

        self.assertEqual(user.last_authenticated_at, now)
        self.assertEqual(user.current_jti_encrypted, "encrypted-new-jti")
        self.assertIsNone(user.password_verified_at)
        self.assertIsNone(user.mfa_session_uuid)
        self.assertEqual(user.failed_totp_attempts, 0)

        repository.update.assert_awaited_once_with(user)
        write_audit_mock.assert_awaited_once()
        repository.commit.assert_awaited_once()
        emit_mock.assert_awaited_once_with(
            E.USER_TOKEN_ISSUE_COMPLETED,
            session,
            user,
        )

        self.assertEqual(user_id, 42)
        self.assertEqual(auth_token, "auth-token")

    async def test_issues_token_without_exp_when_config_allows(self):
        session = AsyncMock()
        data = self._build_data(disable_exp=True)
        user = self._build_user()

        repository = AsyncMock()
        repository.select.return_value = user

        config = MagicMock()
        config.AUTH_ALLOW_PERMANENT_TOKENS = True

        with (
            patch(
                "app.services.user_token_issue.ORMRepository",
                return_value=repository,
            ),
            patch(
                "app.services.user_token_issue.time.time",
                return_value=1_700_000_100,
            ),
            patch(
                "app.services.user_token_issue.decrypt_string",
                return_value="plain-secret",
            ),
            patch(
                "app.services.user_token_issue.is_totp_correct",
                return_value=True,
            ),
            patch(
                "app.services.user_token_issue.generate_jti",
                return_value="new-jti",
            ),
            patch(
                "app.services.user_token_issue.create_auth_token",
                return_value="auth-token",
            ) as create_token_mock,
            patch(
                "app.services.user_token_issue.encrypt_string",
                return_value="enc-jti",
            ),
            patch(
                "app.services.user_token_issue.get_config",
                return_value=config,
            ),
            patch(
                "app.services.user_token_issue.hooks.emit",
                new=AsyncMock(),
            ),
            patch(
                "app.services.user_token_issue.write_audit",
                new=AsyncMock(),
            ),
        ):
            await issue_token(session, data)

        create_token_mock.assert_called_once_with(
            42,
            "new-jti",
            disable_exp=True,
        )

    async def test_issues_regular_token_disable_exp_requested_config_disabled(
        self,
    ):
        session = AsyncMock()
        data = self._build_data(disable_exp=True)
        user = self._build_user()

        repository = AsyncMock()
        repository.select.return_value = user

        config = MagicMock()
        config.AUTH_ALLOW_PERMANENT_TOKENS = False

        with (
            patch(
                "app.services.user_token_issue.ORMRepository",
                return_value=repository,
            ),
            patch(
                "app.services.user_token_issue.time.time",
                return_value=1_700_000_100,
            ),
            patch(
                "app.services.user_token_issue.decrypt_string",
                return_value="plain-secret",
            ),
            patch(
                "app.services.user_token_issue.is_totp_correct",
                return_value=True,
            ),
            patch(
                "app.services.user_token_issue.generate_jti",
                return_value="new-jti",
            ),
            patch(
                "app.services.user_token_issue.create_auth_token",
                return_value="auth-token",
            ) as create_token_mock,
            patch(
                "app.services.user_token_issue.encrypt_string",
                return_value="enc-jti",
            ),
            patch(
                "app.services.user_token_issue.get_config",
                return_value=config,
            ),
            patch(
                "app.services.user_token_issue.hooks.emit",
                new=AsyncMock(),
            ),
            patch(
                "app.services.user_token_issue.write_audit",
                new=AsyncMock(),
            ),
        ):
            await issue_token(session, data)

        create_token_mock.assert_called_once_with(
            42,
            "new-jti",
            disable_exp=False,
        )
