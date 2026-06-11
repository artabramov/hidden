# tests/services/test_user_recovery_code_rotate.py
# SPDX-License-Identifier: GPL-3.0-only

import unittest
from unittest.mock import AsyncMock, MagicMock, patch

from app.constants import OBSCURED_VALUE
from app.errors import ValueInvalidError
from app.events import Events as E
from app.models.user import User
from app.services.user_recovery_code_rotate import rotate_recovery_code

_CANON = "ABCD-ABCD-ABCD-ABCD-ABCD-ABCD"


class TestRotateRecoveryCode(unittest.IsolatedAsyncioTestCase):
    def _build_data(self, recovery_code=_CANON):
        data = MagicMock()
        data.recovery_code = recovery_code
        return data

    def _build_user(self):
        user = MagicMock(spec=User)
        user.password_hash = "stored-password-hash"
        user.password_verified_at = 1_700_000_000
        user.current_jti_encrypted = "old-encrypted-jti"
        user.recovery_code_hash = "old-recovery-hash"
        user.failed_recovery_code_attempts = 3
        return user

    async def test_raises_value_invalid_when_recovery_code_incorrect(self):
        session = AsyncMock()
        user = self._build_user()
        data = self._build_data()

        with (
            patch(
                "app.services.user_recovery_code_rotate.is_password_correct",
                return_value=False,
            ) as is_password_correct_mock,
            patch(
                "app.services.user_recovery_code_rotate."
                "generate_recovery_code",
            ) as generate_mock,
            patch(
                "app.services.user_recovery_code_rotate.hash_string",
            ) as hash_string_mock,
            patch(
                "app.services.user_recovery_code_rotate.generate_jti",
            ) as generate_jti_mock,
            patch(
                "app.services.user_recovery_code_rotate.encrypt_string",
            ) as encrypt_string_mock,
            patch(
                "app.services.user_recovery_code_rotate.ORMRepository",
            ) as repository_cls_mock,
            patch(
                "app.services.user_recovery_code_rotate.hooks.emit",
                new=AsyncMock(),
            ) as emit_mock,
        ):
            with self.assertRaises(ValueInvalidError) as cm:
                await rotate_recovery_code(session, user, data)

        is_password_correct_mock.assert_called_once_with(
            _CANON,
            "old-recovery-hash",
        )
        generate_mock.assert_not_called()
        hash_string_mock.assert_not_called()
        generate_jti_mock.assert_not_called()
        encrypt_string_mock.assert_not_called()
        repository_cls_mock.assert_not_called()
        emit_mock.assert_not_awaited()

        self.assertEqual(user.recovery_code_hash, "old-recovery-hash")
        self.assertEqual(user.failed_recovery_code_attempts, 3)
        self.assertEqual(user.password_verified_at, 1_700_000_000)
        self.assertEqual(user.current_jti_encrypted, "old-encrypted-jti")

        error = cm.exception
        self.assertEqual(error.loc, ("body", "recovery_code"))
        self.assertEqual(error.error_type, "value_invalid")
        self.assertEqual(error.input_value, OBSCURED_VALUE)

    async def test_rotates_recovery_resets_counters_rotates_jti_emits_hook(
        self,
    ):
        session = AsyncMock()
        user = self._build_user()
        data = self._build_data()

        repository = AsyncMock()

        with (
            patch(
                "app.services.user_recovery_code_rotate.is_password_correct",
                return_value=True,
            ) as is_password_correct_mock,
            patch(
                "app.services.user_recovery_code_rotate."
                "generate_recovery_code",
                return_value="WXYZ-WXYZ-WXYZ-WXYZ-WXYZ-WXYZ",
            ) as generate_mock,
            patch(
                "app.services.user_recovery_code_rotate.hash_string",
                return_value="new-recovery-hash",
            ) as hash_string_mock,
            patch(
                "app.services.user_recovery_code_rotate.generate_jti",
                return_value="new-jti",
            ) as generate_jti_mock,
            patch(
                "app.services.user_recovery_code_rotate.encrypt_string",
                return_value="new-encrypted-jti",
            ) as encrypt_string_mock,
            patch(
                "app.services.user_recovery_code_rotate.ORMRepository",
                return_value=repository,
            ) as repository_cls_mock,
            patch(
                "app.services.user_recovery_code_rotate.hooks.emit",
                new=AsyncMock(),
            ) as emit_mock,
            patch(
                "app.services.user_recovery_code_rotate.write_audit",
                new=AsyncMock(),
            ) as write_audit_mock,
        ):
            out = await rotate_recovery_code(session, user, data)

        self.assertEqual(out, "WXYZ-WXYZ-WXYZ-WXYZ-WXYZ-WXYZ")

        is_password_correct_mock.assert_called_once_with(
            _CANON,
            "old-recovery-hash",
        )
        generate_mock.assert_called_once_with()
        hash_string_mock.assert_called_once_with(
            "WXYZ-WXYZ-WXYZ-WXYZ-WXYZ-WXYZ",
        )
        generate_jti_mock.assert_called_once_with()
        encrypt_string_mock.assert_called_once_with("new-jti")
        repository_cls_mock.assert_called_once_with(session)

        self.assertEqual(user.recovery_code_hash, "new-recovery-hash")
        self.assertEqual(user.failed_recovery_code_attempts, 0)
        self.assertIsNone(user.password_verified_at)
        self.assertEqual(user.current_jti_encrypted, "new-encrypted-jti")

        repository.update.assert_awaited_once_with(user)
        write_audit_mock.assert_awaited_once()
        repository.commit.assert_awaited_once()
        emit_mock.assert_awaited_once_with(
            E.USER_RECOVERY_CODE_ROTATE_COMPLETED,
            session,
            user,
        )
