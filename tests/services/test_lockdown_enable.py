# tests/services/test_lockdown_enable.py
# SPDX-License-Identifier: SSPL-1.0

import unittest
from unittest.mock import AsyncMock, MagicMock, patch

from app.constants import (
    LOCKDOWN_MODE_ENABLED_FLAG_PATH,
    OBSCURED_VALUE,
)
from app.errors import (
    ResourceConflictError,
    ResourceNotFoundError,
    TooManyRequestsError,
    ValueInvalidError,
)
from app.events import Events as E
from app.locks import LockType
from app.services.lockdown_enable import enable_lockdown


class TestEnableLockdown(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self._rate_gate_patcher = patch(
            "app.services.lockdown_enable."
            "is_master_password_attempt_throttled",
            new_callable=AsyncMock,
            return_value=False,
        )
        self._rate_gate_patcher.start()

    def tearDown(self):
        self._rate_gate_patcher.stop()

    def _build_lock_context(self):
        lock_context = AsyncMock()
        lock_context.__aenter__.return_value = None
        lock_context.__aexit__.return_value = None
        return lock_context

    def _build_config(self):
        config = MagicMock()
        config.GOCRYPTFS_PASSPHRASE_ENCRYPTED_PATH = (
            "/fake/passphrase.enc"
        )
        return config

    async def test_raises_resource_conflict_when_lockdown_already_enabled(
        self,
    ):
        config = self._build_config()
        lock_context = self._build_lock_context()

        with (
            patch(
                "app.services.lockdown_enable.get_config",
                return_value=config,
            ),
            patch(
                "app.services.lockdown_enable.locks.lock_file",
                return_value=lock_context,
            ) as lock_file_mock,
            patch(
                "app.services.lockdown_enable.isfile",
                new=AsyncMock(return_value=True),
            ) as isfile_mock,
            patch(
                "app.services.lockdown_enable.read",
                new=AsyncMock(),
            ) as read_mock,
            patch(
                "app.services.lockdown_enable.touch",
                new=AsyncMock(),
            ) as touch_mock,
            patch(
                "app.services.lockdown_enable.decrypt_passphrase",
            ) as decrypt_mock,
            patch(
                "app.services.lockdown_enable.hooks.emit",
                new=AsyncMock(),
            ) as emit_mock,
        ):
            with self.assertRaises(ResourceConflictError):
                await enable_lockdown("master-password")

        lock_file_mock.assert_called_once_with(
            LOCKDOWN_MODE_ENABLED_FLAG_PATH,
            LockType.WRITE,
        )
        isfile_mock.assert_awaited_once_with(
            LOCKDOWN_MODE_ENABLED_FLAG_PATH,
        )
        read_mock.assert_not_awaited()
        touch_mock.assert_not_awaited()
        decrypt_mock.assert_not_called()
        emit_mock.assert_not_awaited()

    async def test_raises_resource_not_found_when_passphrase_missing(self):
        config = self._build_config()
        lock_context = self._build_lock_context()

        isfile_mock = AsyncMock(side_effect=[False, False])

        with (
            patch(
                "app.services.lockdown_enable.get_config",
                return_value=config,
            ),
            patch(
                "app.services.lockdown_enable.locks.lock_file",
                return_value=lock_context,
            ) as lock_file_mock,
            patch(
                "app.services.lockdown_enable.isfile",
                new=isfile_mock,
            ),
            patch(
                "app.services.lockdown_enable.read",
                new=AsyncMock(),
            ) as read_mock,
            patch(
                "app.services.lockdown_enable.touch",
                new=AsyncMock(),
            ) as touch_mock,
            patch(
                "app.services.lockdown_enable.decrypt_passphrase",
            ) as decrypt_mock,
            patch(
                "app.services.lockdown_enable.hooks.emit",
                new=AsyncMock(),
            ) as emit_mock,
        ):
            with self.assertRaises(ResourceNotFoundError):
                await enable_lockdown("master-password")

        lock_file_mock.assert_called_once_with(
            LOCKDOWN_MODE_ENABLED_FLAG_PATH,
            LockType.WRITE,
        )
        self.assertEqual(isfile_mock.await_count, 2)
        isfile_mock.assert_any_await(LOCKDOWN_MODE_ENABLED_FLAG_PATH)
        isfile_mock.assert_any_await(
            config.GOCRYPTFS_PASSPHRASE_ENCRYPTED_PATH,
        )
        read_mock.assert_not_awaited()
        touch_mock.assert_not_awaited()
        decrypt_mock.assert_not_called()
        emit_mock.assert_not_awaited()

    async def test_raises_value_invalid_when_master_password_incorrect(self):
        config = self._build_config()
        lock_context = self._build_lock_context()

        isfile_mock = AsyncMock(side_effect=[False, True])

        with (
            patch(
                "app.services.lockdown_enable.get_config",
                return_value=config,
            ),
            patch(
                "app.services.lockdown_enable.locks.lock_file",
                return_value=lock_context,
            ) as lock_file_mock,
            patch(
                "app.services.lockdown_enable.isfile",
                new=isfile_mock,
            ),
            patch(
                "app.services.lockdown_enable.read",
                new=AsyncMock(return_value=b"encrypted-passphrase"),
            ) as read_mock,
            patch(
                "app.services.lockdown_enable.decrypt_passphrase",
                side_effect=ValueError,
            ) as decrypt_mock,
            patch(
                "app.services.lockdown_enable.touch",
                new=AsyncMock(),
            ) as touch_mock,
            patch(
                "app.services.lockdown_enable.hooks.emit",
                new=AsyncMock(),
            ) as emit_mock,
        ):
            with self.assertRaises(ValueInvalidError) as cm:
                await enable_lockdown("wrong-password")

        lock_file_mock.assert_called_once_with(
            LOCKDOWN_MODE_ENABLED_FLAG_PATH,
            LockType.WRITE,
        )
        self.assertEqual(isfile_mock.await_count, 2)
        read_mock.assert_awaited_once_with(
            config.GOCRYPTFS_PASSPHRASE_ENCRYPTED_PATH,
        )
        decrypt_mock.assert_called_once_with(
            b"encrypted-passphrase",
            b"wrong-password",
        )
        touch_mock.assert_not_awaited()
        emit_mock.assert_not_awaited()

        error = cm.exception
        self.assertEqual(error.loc, ("body", "master_password"))
        self.assertEqual(error.error_type, "value_invalid")
        self.assertEqual(error.input_value, OBSCURED_VALUE)

    async def test_enables_lockdown_touches_flag_and_emits_hook(self):
        config = self._build_config()
        lock_context = self._build_lock_context()

        isfile_mock = AsyncMock(side_effect=[False, True])

        with (
            patch(
                "app.services.lockdown_enable.get_config",
                return_value=config,
            ),
            patch(
                "app.services.lockdown_enable.locks.lock_file",
                return_value=lock_context,
            ) as lock_file_mock,
            patch(
                "app.services.lockdown_enable.isfile",
                new=isfile_mock,
            ),
            patch(
                "app.services.lockdown_enable.read",
                new=AsyncMock(return_value=b"encrypted-passphrase"),
            ) as read_mock,
            patch(
                "app.services.lockdown_enable.decrypt_passphrase",
                return_value=b"decrypted-passphrase",
            ) as decrypt_mock,
            patch(
                "app.services.lockdown_enable.touch",
                new=AsyncMock(),
            ) as touch_mock,
            patch(
                "app.services.lockdown_enable.hooks.emit",
                new=AsyncMock(),
            ) as emit_mock,
        ):
            await enable_lockdown("master-password")

        lock_file_mock.assert_called_once_with(
            LOCKDOWN_MODE_ENABLED_FLAG_PATH,
            LockType.WRITE,
        )
        self.assertEqual(isfile_mock.await_count, 2)
        isfile_mock.assert_any_await(LOCKDOWN_MODE_ENABLED_FLAG_PATH)
        isfile_mock.assert_any_await(
            config.GOCRYPTFS_PASSPHRASE_ENCRYPTED_PATH,
        )
        read_mock.assert_awaited_once_with(
            config.GOCRYPTFS_PASSPHRASE_ENCRYPTED_PATH,
        )
        decrypt_mock.assert_called_once_with(
            b"encrypted-passphrase",
            b"master-password",
        )
        touch_mock.assert_awaited_once_with(
            LOCKDOWN_MODE_ENABLED_FLAG_PATH,
        )
        emit_mock.assert_awaited_once_with(E.LOCKDOWN_ENABLE_COMPLETED)

    async def test_raises_too_many_requests_when_rate_gate_blocks(self):
        with patch(
            "app.services.lockdown_enable."
            "is_master_password_attempt_throttled",
            new_callable=AsyncMock,
            return_value=True,
        ):
            with patch(
                "app.services.lockdown_enable.locks.lock_file",
            ) as lock_mock:
                with self.assertRaises(TooManyRequestsError):
                    await enable_lockdown("any-password")
        lock_mock.assert_not_called()
