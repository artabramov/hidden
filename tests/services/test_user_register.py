# tests/services/test_user_register.py
# SPDX-License-Identifier: GPL-3.0-only

import unittest
from unittest.mock import AsyncMock, MagicMock, call, patch

from sqlalchemy.exc import IntegrityError

from app.constants import (
    AUTH_FIRST_ADMIN_LOCK_FLAG_PATH,
    REGISTER_ATTEMPTS_LIMIT,
    REGISTER_ATTEMPTS_WINDOW_SECONDS,
)
from app.errors import TooManyRequestsError, ValueConflictError
from app.events import Events as E
from app.locks import LockType
from app.models.user import User, UserRole
from app.services.user_register import register_user


class TestRegisterUser(unittest.IsolatedAsyncioTestCase):
    def _build_data(self):
        data = MagicMock()
        data.username = "alice"
        data.password = "secret-password"
        data.display_name = "Alice"
        data.summary = "Profile summary"
        return data

    def _build_lock_context(self):
        lock_context = AsyncMock()
        lock_context.__aenter__.return_value = None
        lock_context.__aexit__.return_value = None
        return lock_context

    async def test_raises_value_conflict_when_username_already_exists(self):
        session = AsyncMock()
        data = self._build_data()

        repository = AsyncMock()
        repository.select.return_value = MagicMock(spec=User)

        with (
            patch(
                "app.services.user_register.ORMRepository",
                return_value=repository,
            ),
            patch(
                "app.services.user_register.locks.lock_file",
            ) as lock_file_mock,
            patch(
                "app.services.user_register.hooks.emit",
                new=AsyncMock(),
            ) as emit_mock,
            patch(
                "app.services.user_register.generate_totp_secret",
            ) as generate_totp_secret_mock,
            patch(
                "app.services.user_register.generate_recovery_code",
            ) as generate_recovery_code_mock,
        ):
            with self.assertRaises(ValueConflictError) as cm:
                await register_user(session, data)

        repository.select.assert_awaited_once_with(
            User,
            username="alice",
        )
        repository.count_all.assert_not_awaited()
        repository.insert.assert_not_awaited()
        repository.rollback.assert_not_awaited()
        repository.commit.assert_not_awaited()

        lock_file_mock.assert_not_called()
        generate_totp_secret_mock.assert_not_called()
        generate_recovery_code_mock.assert_not_called()
        emit_mock.assert_not_awaited()

        error = cm.exception
        self.assertEqual(error.loc, ("body", "username"))
        self.assertEqual(error.error_type, "value_conflict")
        self.assertEqual(error.input_value, "alice")

    async def test_raises_too_many_requests_when_recent_users_limit(self):
        session = AsyncMock()
        data = self._build_data()

        repository = AsyncMock()
        repository.select.return_value = None
        repository.count_all.side_effect = [REGISTER_ATTEMPTS_LIMIT]

        lock_context = self._build_lock_context()
        now = 1_700_000_100

        with (
            patch(
                "app.services.user_register.ORMRepository",
                return_value=repository,
            ),
            patch(
                "app.services.user_register.generate_totp_secret",
                return_value="totp-secret",
            ) as generate_totp_secret_mock,
            patch(
                "app.services.user_register.generate_recovery_code",
                return_value="WXYZ-WXYZ-WXYZ-WXYZ-WXYZ-WXYZ",
            ) as generate_recovery_code_mock,
            patch(
                "app.services.user_register.time.time",
                return_value=now,
            ),
            patch(
                "app.services.user_register.locks.lock_file",
                return_value=lock_context,
            ) as lock_file_mock,
            patch(
                "app.services.user_register.hooks.emit",
                new=AsyncMock(),
            ) as emit_mock,
        ):
            with self.assertRaises(TooManyRequestsError):
                await register_user(session, data)

        repository.select.assert_awaited_once_with(
            User,
            username="alice",
        )
        generate_totp_secret_mock.assert_called_once_with()
        generate_recovery_code_mock.assert_called_once_with()

        lock_file_mock.assert_called_once_with(
            AUTH_FIRST_ADMIN_LOCK_FLAG_PATH,
            LockType.WRITE,
        )

        repository.count_all.assert_awaited_once_with(
            User,
            created_at__gt=now - REGISTER_ATTEMPTS_WINDOW_SECONDS,
        )
        repository.insert.assert_not_awaited()
        repository.rollback.assert_not_awaited()
        repository.commit.assert_not_awaited()
        emit_mock.assert_not_awaited()

    async def test_registers_first_user_as_active_admin_and_emits_hook(self):
        session = AsyncMock()
        data = self._build_data()

        repository = AsyncMock()
        repository.select.return_value = None
        repository.count_all.side_effect = [0, 0]

        lock_context = self._build_lock_context()
        config = MagicMock()
        config.FIRST_ADMIN_CREATED_FLAG_PATH = (
            "/fake/secrets/first_admin_created.flag"
        )

        with (
            patch(
                "app.services.user_register.ORMRepository",
                return_value=repository,
            ),
            patch(
                "app.services.user_register.generate_totp_secret",
                return_value="totp-secret",
            ) as generate_totp_secret_mock,
            patch(
                "app.services.user_register.generate_recovery_code",
                return_value="WXYZ-WXYZ-WXYZ-WXYZ-WXYZ-WXYZ",
            ) as generate_recovery_code_mock,
            patch(
                "app.services.user_register.hash_string",
                side_effect=["hashed-password", "hashed-recovery"],
            ) as hash_string_mock,
            patch(
                "app.services.user_register.encrypt_string",
                return_value="encrypted-totp-secret",
            ) as encrypt_string_mock,
            patch(
                "app.services.user_register.locks.lock_file",
                return_value=lock_context,
            ) as lock_file_mock,
            patch(
                "app.services.user_register.hooks.emit",
                new=AsyncMock(),
            ) as emit_mock,
            patch(
                "app.services.user_register.time.time",
                return_value=1_700_000_100,
            ),
            patch(
                "app.services.user_register.write_audit",
                new=AsyncMock(),
            ) as write_audit_mock,
            patch(
                "app.services.user_register.get_config",
                return_value=config,
            ),
            patch(
                "app.services.user_register.touch",
                new=AsyncMock(),
            ) as touch_mock,
        ):
            user, totp_secret, recovery_code = await register_user(
                session,
                data,
            )

        repository.select.assert_awaited_once_with(
            User,
            username="alice",
        )
        lock_file_mock.assert_called_once_with(
            AUTH_FIRST_ADMIN_LOCK_FLAG_PATH,
            LockType.WRITE,
        )
        self.assertEqual(repository.count_all.await_count, 2)
        repository.count_all.assert_any_await(
            User,
            created_at__gt=1_700_000_100 - REGISTER_ATTEMPTS_WINDOW_SECONDS,
        )
        repository.count_all.assert_any_await(User)

        generate_totp_secret_mock.assert_called_once_with()
        generate_recovery_code_mock.assert_called_once_with()
        self.assertEqual(
            hash_string_mock.call_args_list,
            [
                call("secret-password"),
                call("WXYZ-WXYZ-WXYZ-WXYZ-WXYZ-WXYZ"),
            ],
        )
        encrypt_string_mock.assert_called_once_with("totp-secret")

        repository.insert.assert_awaited_once()
        repository.rollback.assert_not_awaited()

        insert_args, insert_kwargs = repository.insert.await_args
        created_user = insert_args[0]

        self.assertIsInstance(created_user, User)
        self.assertIs(created_user, user)
        self.assertEqual(created_user.is_active, True)
        self.assertEqual(created_user.role, UserRole.ADMIN.value)
        self.assertEqual(created_user.username, "alice")
        self.assertEqual(created_user.password_hash, "hashed-password")
        self.assertEqual(created_user.display_name, "Alice")
        self.assertEqual(created_user.summary, "Profile summary")
        self.assertEqual(
            created_user.totp_secret_encrypted,
            "encrypted-totp-secret",
        )
        self.assertEqual(created_user.recovery_code_hash, "hashed-recovery")
        self.assertEqual(insert_kwargs, {})
        write_audit_mock.assert_awaited_once()

        emit_mock.assert_awaited_once_with(
            E.USER_REGISTER_COMPLETED,
            session,
            created_user,
        )
        repository.commit.assert_awaited_once()
        touch_mock.assert_awaited_once_with(
            config.FIRST_ADMIN_CREATED_FLAG_PATH,
        )

        self.assertEqual(totp_secret, "totp-secret")
        self.assertEqual(recovery_code, "WXYZ-WXYZ-WXYZ-WXYZ-WXYZ-WXYZ")

    async def test_registers_non_first_user_as_inactive_reader(self):
        session = AsyncMock()
        data = self._build_data()

        repository = AsyncMock()
        repository.select.return_value = None
        repository.count_all.side_effect = [0, 5]

        lock_context = self._build_lock_context()

        with (
            patch(
                "app.services.user_register.ORMRepository",
                return_value=repository,
            ),
            patch(
                "app.services.user_register.generate_totp_secret",
                return_value="totp-secret",
            ),
            patch(
                "app.services.user_register.generate_recovery_code",
                return_value="WXYZ-WXYZ-WXYZ-WXYZ-WXYZ-WXYZ",
            ),
            patch(
                "app.services.user_register.hash_string",
                side_effect=["hashed-password", "hashed-recovery"],
            ),
            patch(
                "app.services.user_register.encrypt_string",
                return_value="encrypted-totp-secret",
            ),
            patch(
                "app.services.user_register.locks.lock_file",
                return_value=lock_context,
            ),
            patch(
                "app.services.user_register.hooks.emit",
                new=AsyncMock(),
            ) as emit_mock,
            patch(
                "app.services.user_register.time.time",
                return_value=1_700_000_100,
            ),
            patch(
                "app.services.user_register.write_audit",
                new=AsyncMock(),
            ) as write_audit_mock,
            patch(
                "app.services.user_register.touch",
                new=AsyncMock(),
            ) as touch_mock,
        ):
            user, totp_secret, recovery_code = await register_user(
                session,
                data,
            )

        repository.insert.assert_awaited_once()
        insert_args, _ = repository.insert.await_args
        created_user = insert_args[0]

        self.assertIs(created_user, user)
        self.assertEqual(created_user.is_active, False)
        self.assertEqual(created_user.role, UserRole.READER.value)
        self.assertEqual(created_user.recovery_code_hash, "hashed-recovery")
        self.assertEqual(totp_secret, "totp-secret")
        self.assertEqual(recovery_code, "WXYZ-WXYZ-WXYZ-WXYZ-WXYZ-WXYZ")
        write_audit_mock.assert_awaited_once()

        emit_mock.assert_awaited_once_with(
            E.USER_REGISTER_COMPLETED,
            session,
            created_user,
        )
        repository.commit.assert_awaited_once()
        touch_mock.assert_not_awaited()

    async def test_rolls_back_raises_value_conflict_on_insert_integrity_error(
        self,
    ):
        session = AsyncMock()
        data = self._build_data()

        repository = AsyncMock()
        repository.select.return_value = None
        repository.count_all.side_effect = [0, 0]
        repository.insert.side_effect = IntegrityError(None, None, None)

        lock_context = self._build_lock_context()

        with (
            patch(
                "app.services.user_register.ORMRepository",
                return_value=repository,
            ),
            patch(
                "app.services.user_register.generate_totp_secret",
                return_value="totp-secret",
            ),
            patch(
                "app.services.user_register.generate_recovery_code",
                return_value="WXYZ-WXYZ-WXYZ-WXYZ-WXYZ-WXYZ",
            ),
            patch(
                "app.services.user_register.hash_string",
                side_effect=["hashed-password", "hashed-recovery"],
            ),
            patch(
                "app.services.user_register.encrypt_string",
                return_value="encrypted-totp-secret",
            ),
            patch(
                "app.services.user_register.locks.lock_file",
                return_value=lock_context,
            ),
            patch(
                "app.services.user_register.hooks.emit",
                new=AsyncMock(),
            ) as emit_mock,
            patch(
                "app.services.user_register.time.time",
                return_value=1_700_000_100,
            ),
            patch(
                "app.services.user_register.touch",
                new=AsyncMock(),
            ) as touch_mock,
        ):
            with self.assertRaises(ValueConflictError) as cm:
                await register_user(session, data)

        repository.select.assert_awaited_once_with(
            User,
            username="alice",
        )
        self.assertEqual(repository.count_all.await_count, 2)
        repository.insert.assert_awaited_once()
        repository.rollback.assert_awaited_once()
        repository.commit.assert_not_awaited()
        emit_mock.assert_not_awaited()
        touch_mock.assert_not_awaited()

        error = cm.exception
        self.assertEqual(error.loc, ("body", "username"))
        self.assertEqual(error.error_type, "value_conflict")
        self.assertEqual(error.input_value, "alice")
