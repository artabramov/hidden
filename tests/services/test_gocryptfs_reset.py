# tests/services/test_gocryptfs_reset.py
# SPDX-License-Identifier: Apache-2.0

import unittest
from contextlib import contextmanager
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, call, patch

from app.errors import UnauthorizedError
from app.locks import lock_manager
from app.services.gocryptfs_reset import gocryptfs_reset

_PASSWORD = "пароль"


def _config():
    config = MagicMock()
    config.GOCRYPTFS_PASSPHRASE_PATH = "/secrets/passphrase"
    config.INSTALL_MOUNTPOINT = "/mount"
    config.INSTALL_CIPHERDIR = "/cipher"
    config.VERSITY_ACCESS_KEY_PATH = "/secrets/access"
    config.VERSITY_SECRET_KEY_PATH = "/secrets/secret"
    return config


class TestGocryptfsReset(unittest.IsolatedAsyncioTestCase):
    def tearDown(self):
        self.assertFalse(lock_manager._lock.locked())

    @contextmanager
    def _patched(self):
        with (
            patch(
                "app.services.gocryptfs_reset.get_config",
                return_value=_config(),
            ),
            patch(
                "app.services.gocryptfs_reset.read",
                new=AsyncMock(return_value=b"encrypted"),
            ) as read,
            patch(
                "app.services.gocryptfs_reset.decrypt_passphrase",
                return_value=b"passphrase",
            ) as decrypt,
            patch(
                "app.services.gocryptfs_reset.versity_stop",
                new=AsyncMock(),
            ) as versity_stop,
            patch(
                "app.services.gocryptfs_reset.ismount",
                new=AsyncMock(return_value=True),
            ) as ismount,
            patch(
                "app.services.gocryptfs_reset.cipherdir_unmount",
                new=AsyncMock(),
            ) as cipherdir_unmount,
            patch(
                "app.services.gocryptfs_reset.isdir",
                new=AsyncMock(return_value=False),
            ) as isdir,
            patch(
                "app.services.gocryptfs_reset.listdir",
                new=AsyncMock(return_value=[]),
            ) as listdir,
            patch(
                "app.services.gocryptfs_reset.rmtree",
                new=AsyncMock(),
            ) as rmtree,
            patch(
                "app.services.gocryptfs_reset.delete",
                new=AsyncMock(),
            ) as delete,
            patch("app.services.gocryptfs_reset.log") as log,
        ):
            yield SimpleNamespace(
                read=read,
                decrypt=decrypt,
                versity_stop=versity_stop,
                ismount=ismount,
                cipherdir_unmount=cipherdir_unmount,
                isdir=isdir,
                listdir=listdir,
                rmtree=rmtree,
                delete=delete,
                log=log,
            )

    def _assert_secrets_deleted(self, mocks):
        self.assertEqual(
            mocks.delete.await_args_list[-3:],
            [
                call("/secrets/passphrase"),
                call("/secrets/access"),
                call("/secrets/secret"),
            ],
        )

    async def test_resets_mounted_storage(self):
        async def read_passphrase(path):
            self.assertTrue(lock_manager._lock.locked())
            self.assertEqual(path, "/secrets/passphrase")
            return b"encrypted"

        with self._patched() as mocks:
            mocks.read.side_effect = read_passphrase
            mocks.isdir.side_effect = [True, True, False]
            mocks.listdir.return_value = ["nested", "note.txt"]
            await gocryptfs_reset(_PASSWORD)

        mocks.decrypt.assert_called_once_with(
            b"encrypted",
            _PASSWORD.encode("utf-8"),
        )
        mocks.versity_stop.assert_awaited_once_with()
        mocks.ismount.assert_awaited_once_with("/mount")
        mocks.cipherdir_unmount.assert_awaited_once_with(
            mountpoint="/mount",
        )
        mocks.listdir.assert_awaited_once_with("/cipher")
        mocks.rmtree.assert_awaited_once_with("/cipher/nested")
        self.assertEqual(
            mocks.delete.await_args_list,
            [
                call("/cipher/note.txt"),
                call("/secrets/passphrase"),
                call("/secrets/access"),
                call("/secrets/secret"),
            ],
        )

    async def test_skips_unmount_and_cipherdir_when_absent(self):
        with self._patched() as mocks:
            mocks.ismount.return_value = False
            await gocryptfs_reset(_PASSWORD)

        mocks.cipherdir_unmount.assert_not_awaited()
        mocks.listdir.assert_not_awaited()
        mocks.rmtree.assert_not_awaited()
        self._assert_secrets_deleted(mocks)

    async def test_continues_when_versity_stop_fails(self):
        with self._patched() as mocks:
            mocks.versity_stop.side_effect = RuntimeError("stop")
            await gocryptfs_reset(_PASSWORD)

        mocks.cipherdir_unmount.assert_awaited_once_with(
            mountpoint="/mount",
        )
        self._assert_secrets_deleted(mocks)

    async def test_stops_when_unmount_fails(self):
        with self._patched() as mocks:
            mocks.cipherdir_unmount.side_effect = OSError("umount")
            with self.assertRaises(OSError):
                await gocryptfs_reset(_PASSWORD)

        mocks.listdir.assert_not_awaited()
        mocks.delete.assert_not_awaited()

    async def test_rejects_invalid_password(self):
        with self._patched() as mocks:
            mocks.decrypt.side_effect = ValueError("bad")
            with self.assertRaises(UnauthorizedError):
                await gocryptfs_reset(_PASSWORD)

        mocks.log.warning.assert_called_once_with("msg=passphrase_invalid")
        mocks.versity_stop.assert_not_awaited()
        mocks.delete.assert_not_awaited()

    async def test_propagates_unexpected_decrypt_error(self):
        with self._patched() as mocks:
            mocks.decrypt.side_effect = OSError("decrypt")
            with self.assertRaises(OSError):
                await gocryptfs_reset(_PASSWORD)

        mocks.log.warning.assert_not_called()
        mocks.versity_stop.assert_not_awaited()
