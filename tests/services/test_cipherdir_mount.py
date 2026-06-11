# tests/services/test_cipherdir_mount.py
# SPDX-License-Identifier: GPL-3.0-only

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
from app.locks import LockType
from app.services.cipherdir_mount import mount_cipherdir
from app.events import Events as E


class TestMountCipherdir(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.log_patcher = patch(
            "app.services.cipherdir_mount.log"
        )
        self.log_mock = self.log_patcher.start()
        self._rate_gate_patcher = patch(
            "app.services.cipherdir_mount."
            "is_master_password_attempt_throttled",
            new_callable=AsyncMock,
            return_value=False,
        )
        self._rate_gate_mock = self._rate_gate_patcher.start()

    def tearDown(self):
        self._rate_gate_patcher.stop()
        self.log_patcher.stop()

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
        config.SQLITE_DIR = "/fake/mountpoint/db"
        config.SQLITE_PATH = "/fake/mountpoint/db/hidden.sqlite"
        config.FILES_DIR = "/fake/mountpoint/files"
        config.FILES_REVISIONS_DIR = "/fake/mountpoint/files/revisions"
        config.FILES_THUMBNAILS_DIR = (
            "/fake/mountpoint/files/thumbnails"
        )
        config.FILES_TMP_DIR = "/fake/mountpoint/tmp"
        return config

    async def test_raises_resource_not_found_when_cipherdir_uninitialized(
        self,
    ):
        config = self._build_config()
        lock_context = self._build_lock_context()

        with (
            patch(
                "app.services.cipherdir_mount.get_config",
                return_value=config,
            ),
            patch(
                "app.services.cipherdir_mount.locks.lock_file",
                return_value=lock_context,
            ) as lock_file_mock,
            patch(
                "app.services.cipherdir_mount.is_gocryptfs_initialized",
                new=AsyncMock(return_value=False),
            ) as initialized_mock,
            patch(
                "app.services.cipherdir_mount.isfile",
                new=AsyncMock(),
            ) as isfile_mock,
            patch(
                "app.services.cipherdir_mount.ismount",
                new=AsyncMock(),
            ) as ismount_mock,
            patch(
                "app.services.cipherdir_mount.read",
                new=AsyncMock(),
            ) as read_mock,
            patch(
                "app.services.cipherdir_mount.isdir",
                new=AsyncMock(),
            ) as isdir_mock,
            patch(
                "app.services.cipherdir_mount.mkdir",
                new=AsyncMock(),
            ) as mkdir_mock,
            patch(
                "app.services.cipherdir_mount.decrypt_passphrase",
            ) as decrypt_mock,
            patch(
                "app.services.cipherdir_mount.mount_gocryptfs",
                new=AsyncMock(),
            ) as mount_mock,
            patch(
                "app.services.cipherdir_mount.unmount_gocryptfs",
                new=AsyncMock(),
            ) as unmount_mock,
            patch(
                "app.services.cipherdir_mount.upgrade_db",
                new=AsyncMock(),
            ) as init_db_mock,
            patch(
                "app.services.cipherdir_mount.hooks.emit",
                new=AsyncMock(),
            ) as emit_mock,
        ):
            with self.assertRaises(ResourceNotFoundError):
                await mount_cipherdir("master-password")

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
        isdir_mock.assert_not_awaited()
        mkdir_mock.assert_not_awaited()
        decrypt_mock.assert_not_called()
        mount_mock.assert_not_awaited()
        unmount_mock.assert_not_awaited()
        init_db_mock.assert_not_awaited()
        emit_mock.assert_not_awaited()

    async def test_raises_resource_not_found_when_passphrase_missing(
        self,
    ):
        config = self._build_config()
        lock_context = self._build_lock_context()

        with (
            patch(
                "app.services.cipherdir_mount.get_config",
                return_value=config,
            ),
            patch(
                "app.services.cipherdir_mount.locks.lock_file",
                return_value=lock_context,
            ) as lock_file_mock,
            patch(
                "app.services.cipherdir_mount.is_gocryptfs_initialized",
                new=AsyncMock(return_value=True),
            ) as initialized_mock,
            patch(
                "app.services.cipherdir_mount.isfile",
                new=AsyncMock(return_value=False),
            ) as isfile_mock,
            patch(
                "app.services.cipherdir_mount.ismount",
                new=AsyncMock(),
            ) as ismount_mock,
            patch(
                "app.services.cipherdir_mount.read",
                new=AsyncMock(),
            ) as read_mock,
            patch(
                "app.services.cipherdir_mount.isdir",
                new=AsyncMock(),
            ) as isdir_mock,
            patch(
                "app.services.cipherdir_mount.mkdir",
                new=AsyncMock(),
            ) as mkdir_mock,
            patch(
                "app.services.cipherdir_mount.decrypt_passphrase",
            ) as decrypt_mock,
            patch(
                "app.services.cipherdir_mount.mount_gocryptfs",
                new=AsyncMock(),
            ) as mount_mock,
            patch(
                "app.services.cipherdir_mount.unmount_gocryptfs",
                new=AsyncMock(),
            ) as unmount_mock,
            patch(
                "app.services.cipherdir_mount.upgrade_db",
                new=AsyncMock(),
            ) as init_db_mock,
            patch(
                "app.services.cipherdir_mount.hooks.emit",
                new=AsyncMock(),
            ) as emit_mock,
        ):
            with self.assertRaises(ResourceNotFoundError):
                await mount_cipherdir("master-password")

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
        isdir_mock.assert_not_awaited()
        mkdir_mock.assert_not_awaited()
        decrypt_mock.assert_not_called()
        mount_mock.assert_not_awaited()
        unmount_mock.assert_not_awaited()
        init_db_mock.assert_not_awaited()
        emit_mock.assert_not_awaited()

    async def test_raises_resource_conflict_when_already_mounted(self):
        config = self._build_config()
        lock_context = self._build_lock_context()

        with (
            patch(
                "app.services.cipherdir_mount.get_config",
                return_value=config,
            ),
            patch(
                "app.services.cipherdir_mount.locks.lock_file",
                return_value=lock_context,
            ) as lock_file_mock,
            patch(
                "app.services.cipherdir_mount.is_gocryptfs_initialized",
                new=AsyncMock(return_value=True),
            ) as initialized_mock,
            patch(
                "app.services.cipherdir_mount.isfile",
                new=AsyncMock(return_value=True),
            ) as isfile_mock,
            patch(
                "app.services.cipherdir_mount.ismount",
                new=AsyncMock(return_value=True),
            ) as ismount_mock,
            patch(
                "app.services.cipherdir_mount.read",
                new=AsyncMock(),
            ) as read_mock,
            patch(
                "app.services.cipherdir_mount.isdir",
                new=AsyncMock(),
            ) as isdir_mock,
            patch(
                "app.services.cipherdir_mount.mkdir",
                new=AsyncMock(),
            ) as mkdir_mock,
            patch(
                "app.services.cipherdir_mount.decrypt_passphrase",
            ) as decrypt_mock,
            patch(
                "app.services.cipherdir_mount.mount_gocryptfs",
                new=AsyncMock(),
            ) as mount_mock,
            patch(
                "app.services.cipherdir_mount.unmount_gocryptfs",
                new=AsyncMock(),
            ) as unmount_mock,
            patch(
                "app.services.cipherdir_mount.upgrade_db",
                new=AsyncMock(),
            ) as init_db_mock,
            patch(
                "app.services.cipherdir_mount.hooks.emit",
                new=AsyncMock(),
            ) as emit_mock,
        ):
            with self.assertRaises(ResourceConflictError):
                await mount_cipherdir("master-password")

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
        isdir_mock.assert_not_awaited()
        mkdir_mock.assert_not_awaited()
        decrypt_mock.assert_not_called()
        mount_mock.assert_not_awaited()
        unmount_mock.assert_not_awaited()
        init_db_mock.assert_not_awaited()
        emit_mock.assert_not_awaited()

    async def test_raises_value_invalid_when_master_password_incorrect(
        self,
    ):
        config = self._build_config()
        lock_context = self._build_lock_context()

        with (
            patch(
                "app.services.cipherdir_mount.get_config",
                return_value=config,
            ),
            patch(
                "app.services.cipherdir_mount.locks.lock_file",
                return_value=lock_context,
            ) as lock_file_mock,
            patch(
                "app.services.cipherdir_mount.is_gocryptfs_initialized",
                new=AsyncMock(return_value=True),
            ) as initialized_mock,
            patch(
                "app.services.cipherdir_mount.isfile",
                new=AsyncMock(return_value=True),
            ) as isfile_mock,
            patch(
                "app.services.cipherdir_mount.ismount",
                new=AsyncMock(return_value=False),
            ) as ismount_mock,
            patch(
                "app.services.cipherdir_mount.read",
                new=AsyncMock(return_value=b"encrypted-passphrase"),
            ) as read_mock,
            patch(
                "app.services.cipherdir_mount.isdir",
                new=AsyncMock(),
            ) as isdir_mock,
            patch(
                "app.services.cipherdir_mount.mkdir",
                new=AsyncMock(),
            ) as mkdir_mock,
            patch(
                "app.services.cipherdir_mount.decrypt_passphrase",
                side_effect=ValueError,
            ) as decrypt_mock,
            patch(
                "app.services.cipherdir_mount.mount_gocryptfs",
                new=AsyncMock(),
            ) as mount_mock,
            patch(
                "app.services.cipherdir_mount.unmount_gocryptfs",
                new=AsyncMock(),
            ) as unmount_mock,
            patch(
                "app.services.cipherdir_mount.upgrade_db",
                new=AsyncMock(),
            ) as init_db_mock,
            patch(
                "app.services.cipherdir_mount.hooks.emit",
                new=AsyncMock(),
            ) as emit_mock,
        ):
            with self.assertRaises(ValueInvalidError) as cm:
                await mount_cipherdir("wrong-password")

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
        isdir_mock.assert_not_awaited()
        mkdir_mock.assert_not_awaited()
        mount_mock.assert_not_awaited()
        unmount_mock.assert_not_awaited()
        init_db_mock.assert_not_awaited()
        emit_mock.assert_not_awaited()

        error = cm.exception
        self.assertEqual(error.loc, ("body", "master_password"))
        self.assertEqual(error.error_type, "value_invalid")
        self.assertEqual(error.input_value, OBSCURED_VALUE)

    async def test_creates_mountpoint_when_missing_and_mounts_cipherdir(
        self,
    ):
        config = self._build_config()
        lock_context = self._build_lock_context()

        isdir_mock = AsyncMock(
            side_effect=[
                False,
                True,
                True,
                True,
                True,
                True,
            ]
        )

        with (
            patch(
                "app.services.cipherdir_mount.get_config",
                return_value=config,
            ),
            patch(
                "app.services.cipherdir_mount.locks.lock_file",
                return_value=lock_context,
            ) as lock_file_mock,
            patch(
                "app.services.cipherdir_mount.is_gocryptfs_initialized",
                new=AsyncMock(return_value=True),
            ) as initialized_mock,
            patch(
                "app.services.cipherdir_mount.isfile",
                new=AsyncMock(return_value=True),
            ) as isfile_mock,
            patch(
                "app.services.cipherdir_mount.ismount",
                new=AsyncMock(return_value=False),
            ) as ismount_mock,
            patch(
                "app.services.cipherdir_mount.read",
                new=AsyncMock(return_value=b"encrypted-passphrase"),
            ) as read_mock,
            patch(
                "app.services.cipherdir_mount.isdir",
                new=isdir_mock,
            ),
            patch(
                "app.services.cipherdir_mount.mkdir",
                new=AsyncMock(),
            ) as mkdir_mock,
            patch(
                "app.services.cipherdir_mount.decrypt_passphrase",
                return_value=b"decrypted-passphrase",
            ) as decrypt_mock,
            patch(
                "app.services.cipherdir_mount.mount_gocryptfs",
                new=AsyncMock(),
            ) as mount_mock,
            patch(
                "app.services.cipherdir_mount.unmount_gocryptfs",
                new=AsyncMock(),
            ) as unmount_mock,
            patch(
                "app.services.cipherdir_mount.upgrade_db",
                new=AsyncMock(),
            ) as init_db_mock,
            patch(
                "app.services.cipherdir_mount.check_db_integrity",
                new=AsyncMock(),
            ) as integrity_mock,
            patch(
                "app.services.cipherdir_mount.hooks.emit",
                new=AsyncMock(),
            ) as emit_mock,
        ):
            await mount_cipherdir("master-password")

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
        mkdir_mock.assert_any_await(config.GOCRYPTFS_MOUNTPOINT)
        mount_mock.assert_awaited_once_with(
            passphrase="decrypted-passphrase",
            cipherdir=config.GOCRYPTFS_CIPHERDIR,
            mountpoint=config.GOCRYPTFS_MOUNTPOINT,
        )
        init_db_mock.assert_awaited_once()
        integrity_mock.assert_awaited_once_with(config.SQLITE_PATH)
        unmount_mock.assert_not_awaited()
        emit_mock.assert_awaited_once_with(E.CIPHERDIR_MOUNT_COMPLETED)

    async def test_rolls_back_mount_when_post_mount_step_fails(self):
        config = self._build_config()
        lock_context = self._build_lock_context()

        isdir_mock = AsyncMock(
            side_effect=[
                True,
                True,
                True,
                False,
                True,
                True,
            ]
        )

        mkdir_mock = AsyncMock()
        init_db_mock = AsyncMock()
        init_db_mock.side_effect = RuntimeError("db init failed")

        with (
            patch(
                "app.services.cipherdir_mount.get_config",
                return_value=config,
            ),
            patch(
                "app.services.cipherdir_mount.locks.lock_file",
                return_value=lock_context,
            ),
            patch(
                "app.services.cipherdir_mount.is_gocryptfs_initialized",
                new=AsyncMock(return_value=True),
            ),
            patch(
                "app.services.cipherdir_mount.isfile",
                new=AsyncMock(return_value=True),
            ),
            patch(
                "app.services.cipherdir_mount.ismount",
                new=AsyncMock(return_value=False),
            ),
            patch(
                "app.services.cipherdir_mount.read",
                new=AsyncMock(return_value=b"encrypted-passphrase"),
            ),
            patch(
                "app.services.cipherdir_mount.isdir",
                new=isdir_mock,
            ),
            patch(
                "app.services.cipherdir_mount.mkdir",
                new=mkdir_mock,
            ),
            patch(
                "app.services.cipherdir_mount.decrypt_passphrase",
                return_value=b"decrypted-passphrase",
            ),
            patch(
                "app.services.cipherdir_mount.mount_gocryptfs",
                new=AsyncMock(),
            ) as mount_mock,
            patch(
                "app.services.cipherdir_mount.unmount_gocryptfs",
                new=AsyncMock(),
            ) as unmount_mock,
            patch(
                "app.services.cipherdir_mount.upgrade_db",
                new=init_db_mock,
            ),
            patch(
                "app.services.cipherdir_mount.hooks.emit",
                new=AsyncMock(),
            ) as emit_mock,
        ):
            with self.assertRaises(RuntimeError):
                await mount_cipherdir("master-password")

        mount_mock.assert_awaited_once_with(
            passphrase="decrypted-passphrase",
            cipherdir=config.GOCRYPTFS_CIPHERDIR,
            mountpoint=config.GOCRYPTFS_MOUNTPOINT,
        )
        mkdir_mock.assert_awaited_once_with(config.FILES_REVISIONS_DIR)
        init_db_mock.assert_awaited_once()
        unmount_mock.assert_awaited_once_with(
            config.GOCRYPTFS_MOUNTPOINT,
        )
        emit_mock.assert_not_awaited()

    async def test_logs_rollback_failure_unmount_fails_after_post_mount_error(
        self,
    ):
        config = self._build_config()
        lock_context = self._build_lock_context()

        isdir_mock = AsyncMock(
            side_effect=[
                True,
                True,
                True,
                False,
                True,
                True,
            ]
        )

        mkdir_mock = AsyncMock()
        init_db_mock = AsyncMock()
        init_db_mock.side_effect = RuntimeError("db init failed")

        unmount_mock = AsyncMock(
            side_effect=OSError("unmount failed"),
        )

        with (
            patch(
                "app.services.cipherdir_mount.get_config",
                return_value=config,
            ),
            patch(
                "app.services.cipherdir_mount.locks.lock_file",
                return_value=lock_context,
            ),
            patch(
                "app.services.cipherdir_mount.is_gocryptfs_initialized",
                new=AsyncMock(return_value=True),
            ),
            patch(
                "app.services.cipherdir_mount.isfile",
                new=AsyncMock(return_value=True),
            ),
            patch(
                "app.services.cipherdir_mount.ismount",
                new=AsyncMock(return_value=False),
            ),
            patch(
                "app.services.cipherdir_mount.read",
                new=AsyncMock(return_value=b"encrypted-passphrase"),
            ),
            patch(
                "app.services.cipherdir_mount.isdir",
                new=isdir_mock,
            ),
            patch(
                "app.services.cipherdir_mount.mkdir",
                new=mkdir_mock,
            ),
            patch(
                "app.services.cipherdir_mount.decrypt_passphrase",
                return_value=b"decrypted-passphrase",
            ),
            patch(
                "app.services.cipherdir_mount.mount_gocryptfs",
                new=AsyncMock(),
            ),
            patch(
                "app.services.cipherdir_mount.unmount_gocryptfs",
                new=unmount_mock,
            ),
            patch(
                "app.services.cipherdir_mount.upgrade_db",
                new=init_db_mock,
            ),
            patch(
                "app.services.cipherdir_mount.hooks.emit",
                new=AsyncMock(),
            ) as emit_mock,
        ):
            with self.assertRaises(RuntimeError) as cm:
                await mount_cipherdir("master-password")

        self.assertEqual(cm.exception.args[0], "db init failed")
        mkdir_mock.assert_awaited_once_with(config.FILES_REVISIONS_DIR)
        init_db_mock.assert_awaited_once()
        unmount_mock.assert_awaited_once_with(
            config.GOCRYPTFS_MOUNTPOINT,
        )
        emit_mock.assert_not_awaited()

        self.log_mock.exception.assert_any_call(
            "event=%s",
            E.CIPHERDIR_MOUNT_FAILED,
        )
        self.log_mock.exception.assert_any_call(
            "event=%s",
            E.CIPHERDIR_MOUNT_ROLLBACK_FAILED,
        )

    async def test_mounts_cipherdir_initializes_directories_and_emits_hook(
        self,
    ):
        config = self._build_config()
        lock_context = self._build_lock_context()

        isdir_mock = AsyncMock(
            side_effect=[
                True,
                False,
                False,
                False,
                False,
                False,
            ]
        )

        mkdir_mock = AsyncMock()

        with (
            patch(
                "app.services.cipherdir_mount.get_config",
                return_value=config,
            ),
            patch(
                "app.services.cipherdir_mount.locks.lock_file",
                return_value=lock_context,
            ) as lock_file_mock,
            patch(
                "app.services.cipherdir_mount.is_gocryptfs_initialized",
                new=AsyncMock(return_value=True),
            ) as initialized_mock,
            patch(
                "app.services.cipherdir_mount.isfile",
                new=AsyncMock(return_value=True),
            ) as isfile_mock,
            patch(
                "app.services.cipherdir_mount.ismount",
                new=AsyncMock(return_value=False),
            ) as ismount_mock,
            patch(
                "app.services.cipherdir_mount.read",
                new=AsyncMock(return_value=b"encrypted-passphrase"),
            ) as read_mock,
            patch(
                "app.services.cipherdir_mount.isdir",
                new=isdir_mock,
            ),
            patch(
                "app.services.cipherdir_mount.mkdir",
                new=mkdir_mock,
            ),
            patch(
                "app.services.cipherdir_mount.decrypt_passphrase",
                return_value=b"decrypted-passphrase",
            ) as decrypt_mock,
            patch(
                "app.services.cipherdir_mount.mount_gocryptfs",
                new=AsyncMock(),
            ) as mount_mock,
            patch(
                "app.services.cipherdir_mount.unmount_gocryptfs",
                new=AsyncMock(),
            ) as unmount_mock,
            patch(
                "app.services.cipherdir_mount.upgrade_db",
                new=AsyncMock(),
            ) as init_db_mock,
            patch(
                "app.services.cipherdir_mount.check_db_integrity",
                new=AsyncMock(),
            ) as integrity_mock,
            patch(
                "app.services.cipherdir_mount.hooks.emit",
                new=AsyncMock(),
            ) as emit_mock,
        ):
            await mount_cipherdir("master-password")

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
        mount_mock.assert_awaited_once_with(
            passphrase="decrypted-passphrase",
            cipherdir=config.GOCRYPTFS_CIPHERDIR,
            mountpoint=config.GOCRYPTFS_MOUNTPOINT,
        )
        mkdir_mock.assert_any_await(config.SQLITE_DIR)
        mkdir_mock.assert_any_await(config.FILES_DIR)
        mkdir_mock.assert_any_await(config.FILES_REVISIONS_DIR)
        mkdir_mock.assert_any_await(config.FILES_THUMBNAILS_DIR)
        mkdir_mock.assert_any_await(config.FILES_TMP_DIR)
        self.assertEqual(mkdir_mock.await_count, 5)
        init_db_mock.assert_awaited_once()
        integrity_mock.assert_awaited_once_with(config.SQLITE_PATH)
        unmount_mock.assert_not_awaited()
        emit_mock.assert_awaited_once_with(E.CIPHERDIR_MOUNT_COMPLETED)

    async def test_rolls_back_mount_when_integrity_check_fails(self):
        config = self._build_config()
        lock_context = self._build_lock_context()

        isdir_mock = AsyncMock(
            side_effect=[
                True,
                True,
                True,
                True,
                True,
                True,
            ]
        )

        with (
            patch(
                "app.services.cipherdir_mount.get_config",
                return_value=config,
            ),
            patch(
                "app.services.cipherdir_mount.locks.lock_file",
                return_value=lock_context,
            ),
            patch(
                "app.services.cipherdir_mount.is_gocryptfs_initialized",
                new=AsyncMock(return_value=True),
            ),
            patch(
                "app.services.cipherdir_mount.isfile",
                new=AsyncMock(return_value=True),
            ),
            patch(
                "app.services.cipherdir_mount.ismount",
                new=AsyncMock(return_value=False),
            ),
            patch(
                "app.services.cipherdir_mount.read",
                new=AsyncMock(return_value=b"encrypted-passphrase"),
            ),
            patch(
                "app.services.cipherdir_mount.isdir",
                new=isdir_mock,
            ),
            patch(
                "app.services.cipherdir_mount.mkdir",
                new=AsyncMock(),
            ),
            patch(
                "app.services.cipherdir_mount.decrypt_passphrase",
                return_value=b"decrypted-passphrase",
            ),
            patch(
                "app.services.cipherdir_mount.mount_gocryptfs",
                new=AsyncMock(),
            ) as mount_mock,
            patch(
                "app.services.cipherdir_mount.unmount_gocryptfs",
                new=AsyncMock(),
            ) as unmount_mock,
            patch(
                "app.services.cipherdir_mount.upgrade_db",
                new=AsyncMock(),
            ),
            patch(
                "app.services.cipherdir_mount.check_db_integrity",
                new=AsyncMock(
                    side_effect=RuntimeError(
                        "SQLite integrity check failed: Page 3 is never used"
                    )
                ),
            ),
            patch(
                "app.services.cipherdir_mount.hooks.emit",
                new=AsyncMock(),
            ) as emit_mock,
        ):
            with self.assertRaises(RuntimeError) as cm:
                await mount_cipherdir("master-password")

        self.assertIn("integrity check failed", str(cm.exception))
        mount_mock.assert_awaited_once()
        unmount_mock.assert_awaited_once_with(config.GOCRYPTFS_MOUNTPOINT)
        emit_mock.assert_not_awaited()

    async def test_raises_too_many_requests_when_rate_gate_blocks(self):
        with patch(
            "app.services.cipherdir_mount."
            "is_master_password_attempt_throttled",
            new_callable=AsyncMock,
            return_value=True,
        ):
            with patch(
                "app.services.cipherdir_mount.locks.lock_file",
            ) as lock_mock:
                with self.assertRaises(TooManyRequestsError):
                    await mount_cipherdir("any-password")
        lock_mock.assert_not_called()
