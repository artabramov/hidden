# tests/services/test_user_totp_recover.py
# SPDX-License-Identifier: GPL-3.0-only

import unittest
from unittest.mock import AsyncMock, MagicMock, call, patch

from app.constants import (
    AUTH_FAILED_RECOVERY_CODE_ATTEMPTS,
    AUTH_FAILED_SUSPEND_SECONDS,
)
from app.errors import ResourceConflictError, ValueAuthenticationError
from app.events import Events as E
from app.models.user import User
from app.schemas.user_totp_recover import UserTotpRecoverRequest
from app.services.user_totp_recover import recover_totp

_CANON = "ABCD-ABCD-ABCD-ABCD-ABCD-ABCD"
_WRONG = "ZZZZ-ZZZZ-ZZZZ-ZZZZ-ZZZZ-ZZZZ"


class TestRecoverTotp(unittest.IsolatedAsyncioTestCase):
    _MFA = "mfa-session-" + "x" * 15

    def _build_data(self, recovery_code=_CANON):
        return UserTotpRecoverRequest(
            mfa_session_uuid=self._MFA,
            recovery_code=recovery_code,
        )

    def _build_user(self):
        user = MagicMock(spec=User)
        user.id = 7
        user.is_active = True
        user.suspended_until = None
        user.password_verified_at = 1_700_000_000
        user.mfa_session_uuid = self._MFA
        user.recovery_code_hash = "stored-recovery-hash"
        user.failed_recovery_code_attempts = 0
        user.failed_totp_attempts = 2
        user.totp_secret_encrypted = "old-totp-enc"
        user.current_jti_encrypted = "old-jti"
        return user

    async def test_raises_authentication_error_when_user_not_found(self):
        session = AsyncMock()
        data = self._build_data()

        repository = AsyncMock()
        repository.select.return_value = None

        with patch(
            "app.services.user_totp_recover.ORMRepository",
            return_value=repository,
        ):
            with self.assertRaises(ValueAuthenticationError) as cm:
                await recover_totp(session, data)

        repository.select.assert_awaited_once_with(
            User,
            mfa_session_uuid=self._MFA,
        )
        self.assertEqual(cm.exception.loc, ("body", "recovery_code"))

    async def test_raises_authentication_error_when_user_inactive(self):
        session = AsyncMock()
        data = self._build_data()
        user = self._build_user()
        user.is_active = False

        repository = AsyncMock()
        repository.select.return_value = user

        with patch(
            "app.services.user_totp_recover.ORMRepository",
            return_value=repository,
        ):
            with self.assertRaises(ValueAuthenticationError) as cm:
                await recover_totp(session, data)

        self.assertEqual(cm.exception.loc, ("body", "recovery_code"))
        repository.update.assert_not_awaited()

    async def test_raises_authentication_error_when_user_suspended(self):
        session = AsyncMock()
        data = self._build_data()
        user = self._build_user()
        now = 1_700_000_100
        user.suspended_until = now + 3600

        repository = AsyncMock()
        repository.select.return_value = user

        with (
            patch(
                "app.services.user_totp_recover.ORMRepository",
                return_value=repository,
            ),
            patch(
                "app.services.user_totp_recover.time.time",
                return_value=now,
            ),
        ):
            with self.assertRaises(ValueAuthenticationError) as cm:
                await recover_totp(session, data)

        self.assertEqual(cm.exception.loc, ("body", "recovery_code"))
        repository.update.assert_not_awaited()

    async def test_not_treated_as_suspended_when_suspended_until_equals_now(
        self,
    ):
        """
        Suspension check is strict `> now`; equality means suspension lifted.
        """
        session = AsyncMock()
        data = self._build_data(recovery_code="ZZZZ-ZZZZ-ZZZZ-ZZZZ-ZZZZ-ZZZZ")
        user = self._build_user()
        now = 1_700_000_100
        user.suspended_until = now

        repository = AsyncMock()
        repository.select.return_value = user

        with (
            patch(
                "app.services.user_totp_recover.ORMRepository",
                return_value=repository,
            ),
            patch(
                "app.services.user_totp_recover.time.time",
                return_value=now,
            ),
            patch(
                "app.services.user_totp_recover.is_password_correct",
                return_value=False,
            ) as verify_mock,
            patch(
                "app.services.user_totp_recover.hooks.emit",
                new=AsyncMock(),
            ),
        ):
            with self.assertRaises(ValueAuthenticationError):
                await recover_totp(session, data)

        verify_mock.assert_called_once()

        session = AsyncMock()
        data = self._build_data()
        user = self._build_user()
        user.password_verified_at = None

        repository = AsyncMock()
        repository.select.return_value = user

        with (
            patch(
                "app.services.user_totp_recover.ORMRepository",
                return_value=repository,
            ),
            patch(
                "app.services.user_totp_recover.time.time",
                return_value=1_700_000_100,
            ),
        ):
            with self.assertRaises(ResourceConflictError):
                await recover_totp(session, data)

        self.assertIsNone(user.mfa_session_uuid)
        self.assertIsNone(user.password_verified_at)
        repository.update.assert_awaited_once_with(user)
        repository.commit.assert_awaited_once_with()

    async def test_increments_failed_recovery_on_invalid_code(self):
        session = AsyncMock()
        data = self._build_data(recovery_code=_WRONG)
        user = self._build_user()

        repository = AsyncMock()
        repository.select.return_value = user

        with (
            patch(
                "app.services.user_totp_recover.ORMRepository",
                return_value=repository,
            ),
            patch(
                "app.services.user_totp_recover.time.time",
                return_value=1_700_000_100,
            ),
            patch(
                "app.services.user_totp_recover.is_password_correct",
                return_value=False,
            ) as verify_mock,
            patch(
                "app.services.user_totp_recover.hooks.emit",
                new=AsyncMock(),
            ) as emit_mock,
        ):
            with self.assertRaises(ValueAuthenticationError):
                await recover_totp(session, data)

        verify_mock.assert_called_once_with(_WRONG, "stored-recovery-hash")
        self.assertEqual(user.failed_recovery_code_attempts, 1)
        emit_mock.assert_not_awaited()

    async def test_limit_clears_mfa_and_suspends(self):
        session = AsyncMock()
        data = self._build_data(recovery_code=_WRONG)
        user = self._build_user()
        now = 1_700_000_100
        user.failed_recovery_code_attempts = (
            AUTH_FAILED_RECOVERY_CODE_ATTEMPTS - 1
        )

        repository = AsyncMock()
        repository.select.return_value = user

        with (
            patch(
                "app.services.user_totp_recover.ORMRepository",
                return_value=repository,
            ),
            patch(
                "app.services.user_totp_recover.time.time",
                return_value=now,
            ),
            patch(
                "app.services.user_totp_recover.is_password_correct",
                return_value=False,
            ),
            patch(
                "app.services.user_totp_recover.hooks.emit",
                new=AsyncMock(),
            ) as emit_mock,
        ):
            with self.assertRaises(ValueAuthenticationError):
                await recover_totp(session, data)

        self.assertEqual(user.failed_recovery_code_attempts, 0)
        self.assertIsNone(user.mfa_session_uuid)
        self.assertIsNone(user.password_verified_at)
        self.assertEqual(
            user.suspended_until,
            now + AUTH_FAILED_SUSPEND_SECONDS,
        )
        emit_mock.assert_not_awaited()

    async def test_success_rotates_totp_rotates_jti_clears_mfa(self):
        session = AsyncMock()
        data = self._build_data()
        user = self._build_user()

        repository = AsyncMock()
        repository.select.return_value = user
        now = 1_700_000_100

        with (
            patch(
                "app.services.user_totp_recover.ORMRepository",
                return_value=repository,
            ),
            patch(
                "app.services.user_totp_recover.time.time",
                return_value=now,
            ),
            patch(
                "app.services.user_totp_recover.is_password_correct",
                return_value=True,
            ) as verify_mock,
            patch(
                "app.services.user_totp_recover.generate_totp_secret",
                return_value="new-totp-plain",
            ),
            patch(
                "app.services.user_totp_recover.generate_jti",
                return_value="new-jti-plain",
            ) as jti_mock,
            patch(
                "app.services.user_totp_recover.encrypt_string",
                side_effect=["new-totp-enc", "new-jti-enc"],
            ) as enc_mock,
            patch(
                "app.services.user_totp_recover.hooks.emit",
                new=AsyncMock(),
            ) as emit_mock,
            patch(
                "app.services.user_totp_recover.write_audit",
                new=AsyncMock(),
            ) as audit_mock,
        ):
            uid, secret = await recover_totp(session, data)

        verify_mock.assert_called_once_with(_CANON, "stored-recovery-hash")
        jti_mock.assert_called_once_with()
        enc_mock.assert_has_calls(
            [
                call("new-totp-plain"),
                call("new-jti-plain"),
            ],
        )
        self.assertEqual(enc_mock.call_count, 2)
        self.assertEqual(user.totp_secret_encrypted, "new-totp-enc")
        self.assertEqual(user.current_jti_encrypted, "new-jti-enc")
        self.assertIsNone(user.mfa_session_uuid)
        self.assertIsNone(user.password_verified_at)
        self.assertEqual(user.failed_recovery_code_attempts, 0)
        self.assertEqual(user.failed_totp_attempts, 0)

        audit_mock.assert_awaited_once()
        emit_mock.assert_awaited_once_with(
            E.USER_TOTP_RECOVER_COMPLETED,
            session,
            user,
        )
        self.assertEqual(uid, 7)
        self.assertEqual(secret, "new-totp-plain")
