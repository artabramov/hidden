# tests/services/test_cipherdir_unmount.py
# SPDX-License-Identifier: GPL-3.0-only

import sys
import types
import unittest
from unittest.mock import AsyncMock, MagicMock, patch

from app.constants import (
    GOCRYPTFS_CIPHERDIR_LOCK_PATH,
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
from app.services.cipherdir_unmount import unmount_cipherdir


class TestUnmountCipherdir(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        super().setUp()
        self._rate_gate_patcher = patch(
            "app.services.cipherdir_unmount."
            "is_master_password_attempt_throttled",
            new_callable=AsyncMock,
            return_value=False,
        )
        self._rate_gate_patcher.start()
        self.addCleanup(self._rate_gate_patcher.stop)

        self.thumbnail_cache_mock = MagicMock()
        self._thumbnail_cache_patcher = patch(
            "app.services.cipherdir_unmount.get_thumbnail_cache",
            return_value=self.thumbnail_cache_mock,
        )
        self._thumbnail_cache_patcher.start()
        self.addCleanup(self._thumbnail_cache_patcher.stop)

        # app.db.engine calls get_config() at module level, so we cannot
        # patch it via unittest.mock.patch (the import itself would fail).
        # Instead, inject a fake module into sys.modules before the lazy
        # import inside unmount_cipherdir runs, then restore afterwards.
        self.engine_mock = MagicMock()
        self._original_engine_module = sys.modules.get("app.db.engine")
        fake_engine_module = types.ModuleType("app.db.engine")
        fake_engine_module.engine = self.engine_mock
        sys.modules["app.db.engine"] = fake_engine_module
        self.addCleanup(self._restore_engine_module)

    def _restore_engine_module(self):
        if self._original_engine_module is not None:
            sys.modules["app.db.engine"] = self._original_engine_module
        else:
            sys.modules.pop("app.db.engine", None)

    def _build_lock_context(self):
        lock_context = AsyncMock()
        lock_context.__aenter__.return_value = None
        lock_context.__aexit__.return_value = None
        return lock_context

    def _build_config(self):
        config = MagicMock()
        config.GOCRYPTFS_CIPHERDIR = "/fake/cipherdir"
        config.GOCRYPTFS_MOUNTPOINT = "/fake/mountpoint"
        config.GOCRYPTFS_PASSPHRASE_ENCRYPTED_PATH = (
            "/fake/passphrase.enc"
        )
        return config

    async def test_raises_resource_not_found_when_cipherdir_uninitialized(
        self,
    ):
        config = self._build_config()
        lock_context = self._build_lock_context()

        with (
            patch(
                "app.services.cipherdir_unmount.get_config",
                return_value=config,
            ),
            patch(
                "app.services.cipherdir_unmount.locks.lock_file",
                return_value=lock_context,
            ) as lock_file_mock,
            patch(
                "app.services.cipherdir_unmount.is_gocryptfs_initialized",
                new=AsyncMock(return_value=False),
            ) as initialized_mock,
            patch(
                "app.services.cipherdir_unmount.isfile",
                new=AsyncMock(),
            ) as isfile_mock,
            patch(
                "app.services.cipherdir_unmount.ismount",
                new=AsyncMock(),
            ) as ismount_mock,
            patch(
                "app.services.cipherdir_unmount.read",
                new=AsyncMock(),
            ) as read_mock,
            patch(
                "app.services.cipherdir_unmount.decrypt_passphrase",
            ) as decrypt_mock,
            patch(
                "app.services.cipherdir_unmount.unmount_gocryptfs",
                new=AsyncMock(),
            ) as unmount_mock,
            patch(
                "app.services.cipherdir_unmount.hooks.emit",
                new=AsyncMock(),
            ) as emit_mock,
        ):
            with self.assertRaises(ResourceNotFoundError):
                await unmount_cipherdir("master-password")

        lock_file_mock.assert_called_once_with(
            GOCRYPTFS_CIPHERDIR_LOCK_PATH,
            LockType.WRITE,
        )
        initialized_mock.assert_awaited_once_with(
            config.GOCRYPTFS_CIPHERDIR,
        )
        isfile_mock.assert_not_awaited()
        ismount_mock.assert_not_awaited()
        read_mock.assert_not_awaited()
        decrypt_mock.assert_not_called()
        unmount_mock.assert_not_awaited()
        emit_mock.assert_not_awaited()

    async def test_raises_resource_not_found_when_passphrase_missing(
        self,
    ):
        config = self._build_config()
        lock_context = self._build_lock_context()

        with (
            patch(
                "app.services.cipherdir_unmount.get_config",
                return_value=config,
            ),
            patch(
                "app.services.cipherdir_unmount.locks.lock_file",
                return_value=lock_context,
            ) as lock_file_mock,
            patch(
                "app.services.cipherdir_unmount.is_gocryptfs_initialized",
                new=AsyncMock(return_value=True),
            ) as initialized_mock,
            patch(
                "app.services.cipherdir_unmount.isfile",
                new=AsyncMock(return_value=False),
            ) as isfile_mock,
            patch(
                "app.services.cipherdir_unmount.ismount",
                new=AsyncMock(),
            ) as ismount_mock,
            patch(
                "app.services.cipherdir_unmount.read",
                new=AsyncMock(),
            ) as read_mock,
            patch(
                "app.services.cipherdir_unmount.decrypt_passphrase",
            ) as decrypt_mock,
            patch(
                "app.services.cipherdir_unmount.unmount_gocryptfs",
                new=AsyncMock(),
            ) as unmount_mock,
            patch(
                "app.services.cipherdir_unmount.hooks.emit",
                new=AsyncMock(),
            ) as emit_mock,
        ):
            with self.assertRaises(ResourceNotFoundError):
                await unmount_cipherdir("master-password")

        lock_file_mock.assert_called_once_with(
            GOCRYPTFS_CIPHERDIR_LOCK_PATH,
            LockType.WRITE,
        )
        initialized_mock.assert_awaited_once_with(
            config.GOCRYPTFS_CIPHERDIR,
        )
        isfile_mock.assert_awaited_once_with(
            config.GOCRYPTFS_PASSPHRASE_ENCRYPTED_PATH,
        )
        ismount_mock.assert_not_awaited()
        read_mock.assert_not_awaited()
        decrypt_mock.assert_not_called()
        unmount_mock.assert_not_awaited()
        emit_mock.assert_not_awaited()

    async def test_raises_resource_conflict_when_mountpoint_not_mounted(
        self,
    ):
        config = self._build_config()
        lock_context = self._build_lock_context()

        with (
            patch(
                "app.services.cipherdir_unmount.get_config",
                return_value=config,
            ),
            patch(
                "app.services.cipherdir_unmount.locks.lock_file",
                return_value=lock_context,
            ) as lock_file_mock,
            patch(
                "app.services.cipherdir_unmount.is_gocryptfs_initialized",
                new=AsyncMock(return_value=True),
            ) as initialized_mock,
            patch(
                "app.services.cipherdir_unmount.isfile",
                new=AsyncMock(return_value=True),
            ) as isfile_mock,
            patch(
                "app.services.cipherdir_unmount.ismount",
                new=AsyncMock(return_value=False),
            ) as ismount_mock,
            patch(
                "app.services.cipherdir_unmount.read",
                new=AsyncMock(),
            ) as read_mock,
            patch(
                "app.services.cipherdir_unmount.decrypt_passphrase",
            ) as decrypt_mock,
            patch(
                "app.services.cipherdir_unmount.unmount_gocryptfs",
                new=AsyncMock(),
            ) as unmount_mock,
            patch(
                "app.services.cipherdir_unmount.hooks.emit",
                new=AsyncMock(),
            ) as emit_mock,
        ):
            with self.assertRaises(ResourceConflictError):
                await unmount_cipherdir("master-password")

        lock_file_mock.assert_called_once_with(
            GOCRYPTFS_CIPHERDIR_LOCK_PATH,
            LockType.WRITE,
        )
        initialized_mock.assert_awaited_once_with(
            config.GOCRYPTFS_CIPHERDIR,
        )
        isfile_mock.assert_awaited_once_with(
            config.GOCRYPTFS_PASSPHRASE_ENCRYPTED_PATH,
        )
        ismount_mock.assert_awaited_once_with(
            config.GOCRYPTFS_MOUNTPOINT,
        )
        read_mock.assert_not_awaited()
        decrypt_mock.assert_not_called()
        unmount_mock.assert_not_awaited()
        emit_mock.assert_not_awaited()

    async def test_raises_value_invalid_when_master_password_incorrect(
        self,
    ):
        config = self._build_config()
        lock_context = self._build_lock_context()

        with (
            patch(
                "app.services.cipherdir_unmount.get_config",
                return_value=config,
            ),
            patch(
                "app.services.cipherdir_unmount.locks.lock_file",
                return_value=lock_context,
            ) as lock_file_mock,
            patch(
                "app.services.cipherdir_unmount.is_gocryptfs_initialized",
                new=AsyncMock(return_value=True),
            ) as initialized_mock,
            patch(
                "app.services.cipherdir_unmount.isfile",
                new=AsyncMock(return_value=True),
            ) as isfile_mock,
            patch(
                "app.services.cipherdir_unmount.ismount",
                new=AsyncMock(return_value=True),
            ) as ismount_mock,
            patch(
                "app.services.cipherdir_unmount.read",
                new=AsyncMock(return_value=b"encrypted-passphrase"),
            ) as read_mock,
            patch(
                "app.services.cipherdir_unmount.decrypt_passphrase",
                side_effect=ValueError,
            ) as decrypt_mock,
            patch(
                "app.services.cipherdir_unmount.unmount_gocryptfs",
                new=AsyncMock(),
            ) as unmount_mock,
            patch(
                "app.services.cipherdir_unmount.hooks.emit",
                new=AsyncMock(),
            ) as emit_mock,
        ):
            with self.assertRaises(ValueInvalidError) as cm:
                await unmount_cipherdir("wrong-password")

        lock_file_mock.assert_called_once_with(
            GOCRYPTFS_CIPHERDIR_LOCK_PATH,
            LockType.WRITE,
        )
        initialized_mock.assert_awaited_once_with(
            config.GOCRYPTFS_CIPHERDIR,
        )
        isfile_mock.assert_awaited_once_with(
            config.GOCRYPTFS_PASSPHRASE_ENCRYPTED_PATH,
        )
        ismount_mock.assert_awaited_once_with(
            config.GOCRYPTFS_MOUNTPOINT,
        )
        read_mock.assert_awaited_once_with(
            config.GOCRYPTFS_PASSPHRASE_ENCRYPTED_PATH,
        )
        decrypt_mock.assert_called_once_with(
            b"encrypted-passphrase",
            b"wrong-password",
        )
        unmount_mock.assert_not_awaited()
        emit_mock.assert_not_awaited()

        error = cm.exception
        self.assertEqual(error.loc, ("body", "master_password"))
        self.assertEqual(error.error_type, "value_invalid")
        self.assertEqual(error.input_value, OBSCURED_VALUE)

    async def test_unmounts_cipherdir_and_emits_hook(self):
        config = self._build_config()
        lock_context = self._build_lock_context()

        with (
            patch(
                "app.services.cipherdir_unmount.get_config",
                return_value=config,
            ),
            patch(
                "app.services.cipherdir_unmount.locks.lock_file",
                return_value=lock_context,
            ) as lock_file_mock,
            patch(
                "app.services.cipherdir_unmount.is_gocryptfs_initialized",
                new=AsyncMock(return_value=True),
            ) as initialized_mock,
            patch(
                "app.services.cipherdir_unmount.isfile",
                new=AsyncMock(return_value=True),
            ) as isfile_mock,
            patch(
                "app.services.cipherdir_unmount.ismount",
                new=AsyncMock(return_value=True),
            ) as ismount_mock,
            patch(
                "app.services.cipherdir_unmount.read",
                new=AsyncMock(return_value=b"encrypted-passphrase"),
            ) as read_mock,
            patch(
                "app.services.cipherdir_unmount.decrypt_passphrase",
                return_value=b"decrypted-passphrase",
            ) as decrypt_mock,
            patch(
                "app.services.cipherdir_unmount.unmount_gocryptfs",
                new=AsyncMock(),
            ) as unmount_mock,
            patch(
                "app.services.cipherdir_unmount.hooks.emit",
                new=AsyncMock(),
            ) as emit_mock,
        ):
            await unmount_cipherdir("master-password")

        lock_file_mock.assert_called_once_with(
            GOCRYPTFS_CIPHERDIR_LOCK_PATH,
            LockType.WRITE,
        )
        initialized_mock.assert_awaited_once_with(
            config.GOCRYPTFS_CIPHERDIR,
        )
        isfile_mock.assert_awaited_once_with(
            config.GOCRYPTFS_PASSPHRASE_ENCRYPTED_PATH,
        )
        ismount_mock.assert_awaited_once_with(
            config.GOCRYPTFS_MOUNTPOINT,
        )
        read_mock.assert_awaited_once_with(
            config.GOCRYPTFS_PASSPHRASE_ENCRYPTED_PATH,
        )
        decrypt_mock.assert_called_once_with(
            b"encrypted-passphrase",
            b"master-password",
        )
        self.engine_mock.sync_engine.dispose.assert_called_once_with()
        unmount_mock.assert_awaited_once_with(
            mountpoint=config.GOCRYPTFS_MOUNTPOINT,
        )
        self.thumbnail_cache_mock.evict_all.assert_called_once_with()
        emit_mock.assert_awaited_once_with(E.CIPHERDIR_UNMOUNT_COMPLETED)

    async def test_engine_dispose_called_before_unmount_gocryptfs(self):
        config = self._build_config()
        lock_context = self._build_lock_context()
        call_order = []

        def record_dispose():
            call_order.append("dispose")

        async def record_unmount(**_kwargs):
            call_order.append("unmount")

        self.engine_mock.sync_engine.dispose.side_effect = record_dispose

        with (
            patch(
                "app.services.cipherdir_unmount.get_config",
                return_value=config,
            ),
            patch(
                "app.services.cipherdir_unmount.locks.lock_file",
                return_value=lock_context,
            ),
            patch(
                "app.services.cipherdir_unmount.is_gocryptfs_initialized",
                new=AsyncMock(return_value=True),
            ),
            patch(
                "app.services.cipherdir_unmount.isfile",
                new=AsyncMock(return_value=True),
            ),
            patch(
                "app.services.cipherdir_unmount.ismount",
                new=AsyncMock(return_value=True),
            ),
            patch(
                "app.services.cipherdir_unmount.read",
                new=AsyncMock(return_value=b"encrypted-passphrase"),
            ),
            patch(
                "app.services.cipherdir_unmount.decrypt_passphrase",
                return_value=b"decrypted-passphrase",
            ),
            patch(
                "app.services.cipherdir_unmount.unmount_gocryptfs",
                new=record_unmount,
            ),
            patch(
                "app.services.cipherdir_unmount.hooks.emit",
                new=AsyncMock(),
            ),
        ):
            await unmount_cipherdir("master-password")

        self.assertEqual(call_order, ["dispose", "unmount"])

    async def test_raises_too_many_requests_when_rate_gate_blocks(self):
        with patch(
            "app.services.cipherdir_unmount."
            "is_master_password_attempt_throttled",
            new_callable=AsyncMock,
            return_value=True,
        ):
            with patch(
                "app.services.cipherdir_unmount.locks.lock_file",
            ) as lock_mock:
                with self.assertRaises(TooManyRequestsError):
                    await unmount_cipherdir("any-password")
        lock_mock.assert_not_called()
