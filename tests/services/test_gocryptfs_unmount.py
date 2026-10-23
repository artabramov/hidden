# tests/services/test_gocryptfs_unmount.py
# SPDX-License-Identifier: Apache-2.0

import unittest
from contextlib import contextmanager
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

from app.errors import ServiceUnavailableError, UnauthorizedError
from app.locks import lock_manager
from app.services.gocryptfs_unmount import gocryptfs_unmount

_PASSWORD = "пароль"


def _config():
    config = MagicMock()
    config.INSTALL_MOUNTPOINT = "/mount"
    config.GOCRYPTFS_PASSPHRASE_PATH = "/secrets/passphrase"
    return config


class TestGocryptfsUnmount(unittest.IsolatedAsyncioTestCase):
    def tearDown(self):
        self.assertFalse(lock_manager._lock.locked())

    @contextmanager
    def _patched(self):
        with (
            patch(
                "app.services.gocryptfs_unmount.get_config",
                return_value=_config(),
            ),
            patch(
                "app.services.gocryptfs_unmount.ismount",
                new=AsyncMock(return_value=True),
            ) as ismount,
            patch(
                "app.services.gocryptfs_unmount.read",
                new=AsyncMock(return_value=b"encrypted"),
            ) as read,
            patch(
                "app.services.gocryptfs_unmount.decrypt_passphrase",
                return_value=b"passphrase",
            ) as decrypt,
            patch(
                "app.services.gocryptfs_unmount.versity_stop",
                new=AsyncMock(),
            ) as versity_stop,
            patch(
                "app.services.gocryptfs_unmount.cipherdir_unmount",
                new=AsyncMock(),
            ) as cipherdir_unmount,
            patch("app.services.gocryptfs_unmount.log") as log,
        ):
            yield SimpleNamespace(
                ismount=ismount,
                read=read,
                decrypt=decrypt,
                versity_stop=versity_stop,
                cipherdir_unmount=cipherdir_unmount,
                log=log,
            )

    async def test_unmounts_storage(self):
        async def mounted(path):
            self.assertTrue(lock_manager._lock.locked())
            self.assertEqual(path, "/mount")
            return True

        with self._patched() as mocks:
            mocks.ismount.side_effect = mounted
            await gocryptfs_unmount(_PASSWORD)

        mocks.read.assert_awaited_once_with("/secrets/passphrase")
        mocks.decrypt.assert_called_once_with(
            b"encrypted",
            _PASSWORD.encode("utf-8"),
        )
        mocks.versity_stop.assert_awaited_once_with()
        mocks.cipherdir_unmount.assert_awaited_once_with(
            mountpoint="/mount",
        )
        mocks.log.warning.assert_not_called()

    async def test_rejects_missing_mount(self):
        with self._patched() as mocks:
            mocks.ismount.return_value = False
            with self.assertRaises(ServiceUnavailableError):
                await gocryptfs_unmount(_PASSWORD)

        mocks.log.warning.assert_called_once_with(
            "msg=mountpoint_not_found",
        )
        mocks.read.assert_not_awaited()
        mocks.versity_stop.assert_not_awaited()

    async def test_rejects_invalid_password(self):
        with self._patched() as mocks:
            mocks.decrypt.side_effect = ValueError("bad")
            with self.assertRaises(UnauthorizedError):
                await gocryptfs_unmount(_PASSWORD)

        mocks.log.warning.assert_called_once_with("msg=passphrase_invalid")
        mocks.versity_stop.assert_not_awaited()
        mocks.cipherdir_unmount.assert_not_awaited()

    async def test_propagates_unexpected_decrypt_error(self):
        with self._patched() as mocks:
            mocks.decrypt.side_effect = OSError("decrypt")
            with self.assertRaises(OSError):
                await gocryptfs_unmount(_PASSWORD)

        mocks.log.warning.assert_not_called()
        mocks.versity_stop.assert_not_awaited()

    async def test_unmounts_when_versity_stop_fails(self):
        with self._patched() as mocks:
            mocks.versity_stop.side_effect = RuntimeError("stop")
            await gocryptfs_unmount(_PASSWORD)

        mocks.cipherdir_unmount.assert_awaited_once_with(
            mountpoint="/mount",
        )

    async def test_propagates_unmount_failure(self):
        with self._patched() as mocks:
            mocks.cipherdir_unmount.side_effect = OSError("umount")
            with self.assertRaises(OSError):
                await gocryptfs_unmount(_PASSWORD)
