# tests/services/test_gocryptfs_mount.py
# SPDX-License-Identifier: Apache-2.0

import unittest
from contextlib import contextmanager
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, call, patch

from app.errors import BadGatewayError, UnauthorizedError
from app.locks import lock_manager
from app.services.gocryptfs_mount import gocryptfs_mount

_PASSWORD = "пароль"
_PASSPHRASE = "секрет"


def _config():
    config = MagicMock()
    config.INSTALL_MOUNTPOINT = "/mount"
    config.INSTALL_CIPHERDIR = "/cipher"
    config.GOCRYPTFS_PASSPHRASE_PATH = "/secrets/passphrase"
    config.VERSITY_DATA_PATH = "/mount/data"
    config.VERSITY_IAM_PATH = "/mount/iam"
    config.VERSITY_ACCESS_KEY_PATH = "/secrets/access"
    config.VERSITY_SECRET_KEY_PATH = "/secrets/secret"
    config.VERSITY_HOST = "127.0.0.1"
    config.VERSITY_PORT = 9000
    config.VERSITY_WEBGUI_HOST = "127.0.0.1"
    config.VERSITY_WEBGUI_PORT = 8080
    config.VERSITY_WEBGUI_GATEWAY = "http://127.0.0.1:9000"
    config.VERSITY_WEBGUI_CORS_ALLOW_ORIGIN = "http://localhost:8080"
    return config


class TestGocryptfsMount(unittest.IsolatedAsyncioTestCase):
    def tearDown(self):
        self.assertFalse(lock_manager._lock.locked())

    @contextmanager
    def _patched(self):
        with (
            patch(
                "app.services.gocryptfs_mount.get_config",
                return_value=_config(),
            ),
            patch(
                "app.services.gocryptfs_mount.ismount",
                new=AsyncMock(return_value=False),
            ) as ismount,
            patch(
                "app.services.gocryptfs_mount.read",
                new=AsyncMock(return_value=b"encrypted"),
            ) as read,
            patch(
                "app.services.gocryptfs_mount.versity_read",
                new=AsyncMock(return_value=("access-key", "secret-key")),
            ) as versity_read,
            patch(
                "app.services.gocryptfs_mount.decrypt_passphrase",
                return_value=_PASSPHRASE.encode("utf-8"),
            ) as decrypt,
            patch(
                "app.services.gocryptfs_mount.isdir",
                new=AsyncMock(return_value=True),
            ) as isdir,
            patch(
                "app.services.gocryptfs_mount.mkdir",
                new=AsyncMock(),
            ) as mkdir,
            patch(
                "app.services.gocryptfs_mount.cipherdir_mount",
                new=AsyncMock(),
            ) as cipherdir_mount,
            patch(
                "app.services.gocryptfs_mount.versity_start",
                new=AsyncMock(),
            ) as versity_start,
            patch(
                "app.services.gocryptfs_mount.versity_stop",
                new=AsyncMock(),
            ) as versity_stop,
            patch(
                "app.services.gocryptfs_mount.cipherdir_unmount",
                new=AsyncMock(),
            ) as cipherdir_unmount,
            patch("app.services.gocryptfs_mount.log") as log,
        ):
            yield SimpleNamespace(
                ismount=ismount,
                read=read,
                versity_read=versity_read,
                decrypt=decrypt,
                isdir=isdir,
                mkdir=mkdir,
                cipherdir_mount=cipherdir_mount,
                versity_start=versity_start,
                versity_stop=versity_stop,
                cipherdir_unmount=cipherdir_unmount,
                log=log,
            )

    def _assert_started(self, mocks):
        mocks.cipherdir_mount.assert_awaited_once_with(
            passphrase=_PASSPHRASE,
            cipherdir="/cipher",
            mountpoint="/mount",
        )
        mocks.decrypt.assert_called_once_with(
            b"encrypted",
            _PASSWORD.encode("utf-8"),
        )
        mocks.versity_start.assert_awaited_once_with(
            "127.0.0.1",
            9000,
            "127.0.0.1",
            8080,
            "http://127.0.0.1:9000",
            "http://localhost:8080",
            "/mount/data",
            "/mount/iam",
            "access-key",
            "secret-key",
        )
        mocks.versity_stop.assert_not_awaited()
        mocks.cipherdir_unmount.assert_not_awaited()

    async def test_mounts_existing_directories(self):
        async def unmounted(path):
            self.assertTrue(lock_manager._lock.locked())
            self.assertEqual(path, "/mount")
            return False

        with self._patched() as mocks:
            mocks.ismount.side_effect = unmounted
            await gocryptfs_mount(_PASSWORD)

        self._assert_started(mocks)
        mocks.mkdir.assert_not_awaited()
        mocks.read.assert_awaited_once_with("/secrets/passphrase")
        mocks.versity_read.assert_awaited_once_with(
            "/secrets/access",
            "/secrets/secret",
            _PASSPHRASE,
        )

    async def test_creates_missing_directories(self):
        with self._patched() as mocks:
            mocks.isdir.side_effect = [False, False, False]
            await gocryptfs_mount(_PASSWORD)

        self.assertEqual(
            mocks.mkdir.await_args_list,
            [
                call("/mount"),
                call("/mount/data"),
                call("/mount/iam"),
            ],
        )
        mocks.versity_start.assert_awaited_once()

    async def test_rejects_existing_mount(self):
        with self._patched() as mocks:
            mocks.ismount.return_value = True
            with self.assertRaises(BadGatewayError):
                await gocryptfs_mount(_PASSWORD)

        mocks.log.warning.assert_called_once_with("msg=mountpoint_exists")
        mocks.read.assert_not_awaited()
        mocks.decrypt.assert_not_called()

    async def test_rejects_invalid_password(self):
        with self._patched() as mocks:
            mocks.decrypt.side_effect = ValueError("bad")
            with self.assertRaises(UnauthorizedError):
                await gocryptfs_mount(_PASSWORD)

        mocks.log.warning.assert_called_once_with("msg=passphrase_invalid")
        mocks.cipherdir_mount.assert_not_awaited()

    async def test_propagates_unexpected_decrypt_error(self):
        with self._patched() as mocks:
            mocks.decrypt.side_effect = OSError("decrypt")
            with self.assertRaises(OSError):
                await gocryptfs_mount(_PASSWORD)

        mocks.log.warning.assert_not_called()
        mocks.cipherdir_mount.assert_not_awaited()

    async def test_does_not_roll_back_failed_mount(self):
        with self._patched() as mocks:
            mocks.cipherdir_mount.side_effect = OSError("mount")
            with self.assertRaises(OSError):
                await gocryptfs_mount(_PASSWORD)

        mocks.versity_start.assert_not_awaited()
        mocks.versity_stop.assert_not_awaited()
        mocks.cipherdir_unmount.assert_not_awaited()
        mocks.log.exception.assert_not_called()

    async def test_does_not_roll_back_failed_mountpoint_creation(self):
        with self._patched() as mocks:
            mocks.isdir.return_value = False
            mocks.mkdir.side_effect = OSError("mkdir")
            with self.assertRaises(OSError):
                await gocryptfs_mount(_PASSWORD)

        mocks.cipherdir_mount.assert_not_awaited()
        mocks.cipherdir_unmount.assert_not_awaited()

    async def test_rolls_back_when_versity_fails_to_start(self):
        with self._patched() as mocks:
            mocks.versity_start.side_effect = OSError("start")
            with self.assertRaises(OSError) as caught:
                await gocryptfs_mount(_PASSWORD)

        self.assertEqual(str(caught.exception), "start")
        mocks.versity_stop.assert_awaited_once_with()
        mocks.cipherdir_unmount.assert_awaited_once_with("/mount")
        mocks.log.exception.assert_called_once_with(
            "msg=gocryptfs_mount_failed",
        )
        mocks.log.warning.assert_called_once_with(
            "msg=gocryptfs_mount_rollback_completed",
        )

    async def test_unmounts_when_versity_stop_fails(self):
        with self._patched() as mocks:
            mocks.versity_start.side_effect = OSError("start")
            mocks.versity_stop.side_effect = RuntimeError("stop")
            with self.assertRaises(OSError):
                await gocryptfs_mount(_PASSWORD)

        mocks.cipherdir_unmount.assert_awaited_once_with("/mount")
        mocks.log.warning.assert_called_once_with(
            "msg=gocryptfs_mount_rollback_completed",
        )

    async def test_reports_failed_rollback(self):
        with self._patched() as mocks:
            mocks.versity_start.side_effect = OSError("start")
            mocks.cipherdir_unmount.side_effect = RuntimeError("umount")
            with self.assertRaises(OSError) as caught:
                await gocryptfs_mount(_PASSWORD)

        self.assertEqual(str(caught.exception), "start")
        self.assertEqual(
            mocks.log.exception.call_args_list,
            [
                call("msg=gocryptfs_mount_failed"),
                call("msg=gocryptfs_mount_rollback_failed"),
            ],
        )
        mocks.log.warning.assert_not_called()

    async def test_rolls_back_when_credentials_cannot_be_decrypted(self):
        with self._patched() as mocks:
            mocks.versity_read.side_effect = ValueError("corrupted")
            with self.assertRaises(ValueError):
                await gocryptfs_mount(_PASSWORD)

        mocks.versity_start.assert_not_awaited()
        mocks.versity_stop.assert_awaited_once_with()
        mocks.cipherdir_unmount.assert_awaited_once_with("/mount")

    async def test_rolls_back_when_data_directory_creation_fails(self):
        with self._patched() as mocks:
            mocks.isdir.side_effect = [True, False]
            mocks.mkdir.side_effect = OSError("mkdir")
            with self.assertRaises(OSError):
                await gocryptfs_mount(_PASSWORD)

        mocks.versity_start.assert_not_awaited()
        mocks.cipherdir_unmount.assert_awaited_once_with("/mount")
        mocks.mkdir.assert_awaited_once_with("/mount/data")
