# tests/services/test_user_password_change.py
# SPDX-License-Identifier: GPL-3.0-only

import unittest
from unittest.mock import AsyncMock, MagicMock, patch

from app.constants import OBSCURED_VALUE
from app.errors import ValueInvalidError
from app.events import Events as E
from app.models.user import User
from app.services.user_password_change import change_password


class TestChangePassword(unittest.IsolatedAsyncioTestCase):
    def _build_data(
        self,
        current_password="current-password",
        changed_password="new-password",
    ):
        data = MagicMock()
        data.current_password = current_password
        data.changed_password = changed_password
        return data

    def _build_user(self):
        user = MagicMock(spec=User)
        user.password_hash = "stored-password-hash"
        user.password_verified_at = 1_700_000_000
        user.current_jti_encrypted = "old-encrypted-jti"
        return user

    async def test_raises_value_invalid_when_current_password_incorrect(self):
        session = AsyncMock()
        user = self._build_user()
        data = self._build_data()

        with (
            patch(
                "app.services.user_password_change.is_password_correct",
                return_value=False,
            ) as is_password_correct_mock,
            patch(
                "app.services.user_password_change.hash_string",
            ) as hash_string_mock,
            patch(
                "app.services.user_password_change.generate_jti",
            ) as generate_jti_mock,
            patch(
                "app.services.user_password_change.encrypt_string",
            ) as encrypt_string_mock,
            patch(
                "app.services.user_password_change.ORMRepository",
            ) as repository_cls_mock,
            patch(
                "app.services.user_password_change.hooks.emit",
                new=AsyncMock(),
            ) as emit_mock,
        ):
            with self.assertRaises(ValueInvalidError) as cm:
                await change_password(session, user, data)

        is_password_correct_mock.assert_called_once_with(
            "current-password",
            "stored-password-hash",
        )
        hash_string_mock.assert_not_called()
        generate_jti_mock.assert_not_called()
        encrypt_string_mock.assert_not_called()
        repository_cls_mock.assert_not_called()
        emit_mock.assert_not_awaited()

        self.assertEqual(user.password_hash, "stored-password-hash")
        self.assertEqual(user.password_verified_at, 1_700_000_000)
        self.assertEqual(user.current_jti_encrypted, "old-encrypted-jti")

        error = cm.exception
        self.assertEqual(error.loc, ("body", "current_password"))
        self.assertEqual(error.error_type, "value_invalid")
        self.assertEqual(error.input_value, OBSCURED_VALUE)

    async def test_changes_password_resets_verification_rotates_jti_emits_hook(
        self,
    ):
        session = AsyncMock()
        user = self._build_user()
        data = self._build_data()

        repository = AsyncMock()

        with (
            patch(
                "app.services.user_password_change.is_password_correct",
                return_value=True,
            ) as is_password_correct_mock,
            patch(
                "app.services.user_password_change.hash_string",
                return_value="new-password-hash",
            ) as hash_string_mock,
            patch(
                "app.services.user_password_change.generate_jti",
                return_value="new-jti",
            ) as generate_jti_mock,
            patch(
                "app.services.user_password_change.encrypt_string",
                return_value="new-encrypted-jti",
            ) as encrypt_string_mock,
            patch(
                "app.services.user_password_change.ORMRepository",
                return_value=repository,
            ) as repository_cls_mock,
            patch(
                "app.services.user_password_change.hooks.emit",
                new=AsyncMock(),
            ) as emit_mock,
            patch(
                "app.services.user_password_change.write_audit",
                new=AsyncMock(),
            ) as write_audit_mock,
        ):
            await change_password(session, user, data)

        is_password_correct_mock.assert_called_once_with(
            "current-password",
            "stored-password-hash",
        )
        hash_string_mock.assert_called_once_with("new-password")
        generate_jti_mock.assert_called_once_with()
        encrypt_string_mock.assert_called_once_with("new-jti")
        repository_cls_mock.assert_called_once_with(session)

        self.assertEqual(user.password_hash, "new-password-hash")
        self.assertIsNone(user.password_verified_at)
        self.assertEqual(user.current_jti_encrypted, "new-encrypted-jti")

        repository.update.assert_awaited_once_with(user)
        write_audit_mock.assert_awaited_once()
        repository.commit.assert_awaited_once()
        emit_mock.assert_awaited_once_with(
            E.USER_PASSWORD_CHANGE_COMPLETED,
            session,
            user,
        )

    async def test_allows_same_password_update_per_note_contract(self):
        session = AsyncMock()
        user = self._build_user()
        data = self._build_data(
            current_password="same-password",
            changed_password="same-password",
        )

        repository = AsyncMock()

        with (
            patch(
                "app.services.user_password_change.is_password_correct",
                return_value=True,
            ) as is_password_correct_mock,
            patch(
                "app.services.user_password_change.hash_string",
                return_value="rehash-of-same-password",
            ) as hash_string_mock,
            patch(
                "app.services.user_password_change.generate_jti",
                return_value="rotated-jti",
            ) as generate_jti_mock,
            patch(
                "app.services.user_password_change.encrypt_string",
                return_value="encrypted-rotated-jti",
            ) as encrypt_string_mock,
            patch(
                "app.services.user_password_change.ORMRepository",
                return_value=repository,
            ),
            patch(
                "app.services.user_password_change.hooks.emit",
                new=AsyncMock(),
            ) as emit_mock,
            patch(
                "app.services.user_password_change.write_audit",
                new=AsyncMock(),
            ) as write_audit_mock,
        ):
            await change_password(session, user, data)

        is_password_correct_mock.assert_called_once_with(
            "same-password",
            "stored-password-hash",
        )
        hash_string_mock.assert_called_once_with("same-password")
        generate_jti_mock.assert_called_once_with()
        encrypt_string_mock.assert_called_once_with("rotated-jti")

        self.assertEqual(user.password_hash, "rehash-of-same-password")
        self.assertIsNone(user.password_verified_at)
        self.assertEqual(
            user.current_jti_encrypted,
            "encrypted-rotated-jti",
        )

        repository.update.assert_awaited_once_with(user)
        write_audit_mock.assert_awaited_once()
        repository.commit.assert_awaited_once()
        emit_mock.assert_awaited_once_with(
            E.USER_PASSWORD_CHANGE_COMPLETED,
            session,
            user,
        )
