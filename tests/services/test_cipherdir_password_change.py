# tests/services/test_cipherdir_password_change.py
# SPDX-License-Identifier: GPL-3.0-only

import unittest
from unittest.mock import AsyncMock, MagicMock, patch

from app.constants import (
    OBSCURED_VALUE,
)
from app.errors import (
    ResourceNotFoundError,
    TooManyRequestsError,
    ValueInvalidError,
)
from app.events import Events as E
from app.services.cipherdir_password_change import (
    change_cipherdir_password,
)


class TestChangeCipherdirPassword(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.log_patcher = patch(
            "app.services.cipherdir_password_change.log"
        )
        self.log_patcher.start()
        self._rate_gate_patcher = patch(
            "app.services.cipherdir_password_change."
            "is_master_password_attempt_throttled",
            new_callable=AsyncMock,
            return_value=False,
        )
        self._rate_gate_patcher.start()

    def tearDown(self):
        self._rate_gate_patcher.stop()
        self.log_patcher.stop()

    def _build_lock_context(self):
        ctx = AsyncMock()
        ctx.__aenter__.return_value = None
        ctx.__aexit__.return_value = None
        return ctx

    def _build_config(self):
        config = MagicMock()
        config.GOCRYPTFS_CIPHERDIR = "/fake/cipherdir"
        config.GOCRYPTFS_PASSPHRASE_ENCRYPTED_PATH = (
            "/fake/passphrase.enc"
        )
        return config

    async def test_raises_not_found_when_cipherdir_not_initialized(
        self,
    ):
        config = self._build_config()

        with (
            patch(
                "app.services.cipherdir_password_change.get_config",
                return_value=config,
            ),
            patch(
                "app.services.cipherdir_password_change.locks.lock_file",
                return_value=self._build_lock_context(),
            ),
            patch(
                "app.services.cipherdir_password_change.is_gocryptfs_initialized",  # noqa E501
                new=AsyncMock(return_value=False),
            ) as init_mock,
            patch(
                "app.services.cipherdir_password_change.isfile",
                new=AsyncMock(),
            ) as isfile_mock,
        ):
            with self.assertRaises(ResourceNotFoundError):
                await change_cipherdir_password(
                    "old", "new"
                )

        init_mock.assert_awaited_once_with(config.GOCRYPTFS_CIPHERDIR)
        isfile_mock.assert_not_awaited()

    async def test_raises_not_found_when_passphrase_missing(self):
        config = self._build_config()

        with (
            patch(
                "app.services.cipherdir_password_change.get_config",
                return_value=config,
            ),
            patch(
                "app.services.cipherdir_password_change.locks.lock_file",
                return_value=self._build_lock_context(),
            ),
            patch(
                "app.services.cipherdir_password_change.is_gocryptfs_initialized",  # noqa E501
                new=AsyncMock(return_value=True),
            ),
            patch(
                "app.services.cipherdir_password_change.isfile",
                new=AsyncMock(return_value=False),
            ) as isfile_mock,
        ):
            with self.assertRaises(ResourceNotFoundError):
                await change_cipherdir_password(
                    "old", "new"
                )

        isfile_mock.assert_awaited_once_with(
            config.GOCRYPTFS_PASSPHRASE_ENCRYPTED_PATH,
        )

    async def test_raises_invalid_when_current_password_wrong(self):
        config = self._build_config()

        with (
            patch(
                "app.services.cipherdir_password_change.get_config",
                return_value=config,
            ),
            patch(
                "app.services.cipherdir_password_change.locks.lock_file",
                return_value=self._build_lock_context(),
            ),
            patch(
                "app.services.cipherdir_password_change.is_gocryptfs_initialized",  # noqa E501
                new=AsyncMock(return_value=True),
            ),
            patch(
                "app.services.cipherdir_password_change.isfile",
                new=AsyncMock(return_value=True),
            ),
            patch(
                "app.services.cipherdir_password_change.read",
                new=AsyncMock(return_value=b"encrypted"),
            ),
            patch(
                "app.services.cipherdir_password_change.decrypt_passphrase",
                side_effect=ValueError,
            ) as decrypt_mock,
            patch(
                "app.services.cipherdir_password_change.write",
                new=AsyncMock(),
            ) as write_mock,
            patch(
                "app.services.cipherdir_password_change.hooks.emit",
                new=AsyncMock(),
            ) as emit_mock,
        ):
            with self.assertRaises(ValueInvalidError) as cm:
                await change_cipherdir_password(
                    "wrong", "new"
                )

        decrypt_mock.assert_called_once_with(
            b"encrypted",
            b"wrong",
        )
        write_mock.assert_not_awaited()
        emit_mock.assert_not_awaited()

        err = cm.exception
        self.assertEqual(
            err.loc,
            ("body", "current_master_password"),
        )
        self.assertEqual(err.input_value, OBSCURED_VALUE)

    async def test_reencrypts_and_writes_and_emits_hook(self):
        config = self._build_config()

        with (
            patch(
                "app.services.cipherdir_password_change.get_config",
                return_value=config,
            ),
            patch(
                "app.services.cipherdir_password_change.locks.lock_file",
                return_value=self._build_lock_context(),
            ),
            patch(
                "app.services.cipherdir_password_change.is_gocryptfs_initialized",  # noqa E501
                new=AsyncMock(return_value=True),
            ),
            patch(
                "app.services.cipherdir_password_change.isfile",
                new=AsyncMock(return_value=True),
            ),
            patch(
                "app.services.cipherdir_password_change.read",
                new=AsyncMock(return_value=b"encrypted"),
            ),
            patch(
                "app.services.cipherdir_password_change.decrypt_passphrase",
                return_value=b"plain",
            ) as decrypt_mock,
            patch(
                "app.services.cipherdir_password_change.encrypt_passphrase",
                return_value=b"re-encrypted",
            ) as encrypt_mock,
            patch(
                "app.services.cipherdir_password_change.write",
                new=AsyncMock(),
            ) as write_mock,
            patch(
                "app.services.cipherdir_password_change.hooks.emit",
                new=AsyncMock(),
            ) as emit_mock,
        ):
            await change_cipherdir_password(
                "old", "new"
            )

        decrypt_mock.assert_called_once_with(
            b"encrypted",
            b"old",
        )
        encrypt_mock.assert_called_once_with(
            b"plain",
            b"new",
        )
        write_mock.assert_awaited_once_with(
            config.GOCRYPTFS_PASSPHRASE_ENCRYPTED_PATH,
            b"re-encrypted",
        )
        emit_mock.assert_awaited_once_with(
            E.CIPHERDIR_PASSWORD_CHANGE_COMPLETED,
        )

    async def test_raises_too_many_requests_when_rate_gate_blocks(self):
        with patch(
            "app.services.cipherdir_password_change."
            "is_master_password_attempt_throttled",
            new_callable=AsyncMock,
            return_value=True,
        ):
            with patch(
                "app.services.cipherdir_password_change.locks.lock_file",
            ) as lock_mock:
                with self.assertRaises(TooManyRequestsError):
                    await change_cipherdir_password(
                        "old", "new",
                    )
        lock_mock.assert_not_called()
