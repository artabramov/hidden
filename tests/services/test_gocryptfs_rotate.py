# tests/services/test_gocryptfs_rotate.py
# SPDX-License-Identifier: Apache-2.0

import unittest
from contextlib import contextmanager
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

from app.errors import UnauthorizedError
from app.locks import lock_manager
from app.services.gocryptfs_rotate import gocryptfs_rotate

_CURRENT = "пароль"
_CHANGED = "новый"
_PASSPHRASE = b"\xff\x00secret"


def _config():
    config = MagicMock()
    config.GOCRYPTFS_PASSPHRASE_PATH = "/secrets/passphrase"
    return config


class TestGocryptfsRotate(unittest.IsolatedAsyncioTestCase):
    def tearDown(self):
        self.assertFalse(lock_manager._lock.locked())

    @contextmanager
    def _patched(self):
        with (
            patch(
                "app.services.gocryptfs_rotate.get_config",
                return_value=_config(),
            ),
            patch(
                "app.services.gocryptfs_rotate.read",
                new=AsyncMock(return_value=b"encrypted"),
            ) as read,
            patch(
                "app.services.gocryptfs_rotate.decrypt_passphrase",
                return_value=_PASSPHRASE,
            ) as decrypt,
            patch(
                "app.services.gocryptfs_rotate.encrypt_passphrase",
                return_value=b"rewrapped",
            ) as encrypt,
            patch(
                "app.services.gocryptfs_rotate.write",
                new=AsyncMock(),
            ) as write,
            patch("app.services.gocryptfs_rotate.log") as log,
        ):
            yield SimpleNamespace(
                read=read,
                decrypt=decrypt,
                encrypt=encrypt,
                write=write,
                log=log,
            )

    async def test_rewraps_passphrase(self):
        async def read_passphrase(path):
            self.assertTrue(lock_manager._lock.locked())
            self.assertEqual(path, "/secrets/passphrase")
            return b"encrypted"

        with self._patched() as mocks:
            mocks.read.side_effect = read_passphrase
            await gocryptfs_rotate(_CURRENT, _CHANGED)

        mocks.decrypt.assert_called_once_with(
            b"encrypted",
            _CURRENT.encode("utf-8"),
        )
        mocks.encrypt.assert_called_once_with(
            _PASSPHRASE,
            _CHANGED.encode("utf-8"),
        )
        mocks.write.assert_awaited_once_with(
            "/secrets/passphrase",
            b"rewrapped",
        )
        mocks.log.warning.assert_not_called()

    async def test_rejects_invalid_password(self):
        with self._patched() as mocks:
            mocks.decrypt.side_effect = ValueError("bad")
            with self.assertRaises(UnauthorizedError):
                await gocryptfs_rotate(_CURRENT, _CHANGED)

        mocks.log.warning.assert_called_once_with("msg=passphrase_invalid")
        mocks.encrypt.assert_not_called()
        mocks.write.assert_not_awaited()

    async def test_propagates_unexpected_decrypt_error(self):
        with self._patched() as mocks:
            mocks.decrypt.side_effect = OSError("decrypt")
            with self.assertRaises(OSError):
                await gocryptfs_rotate(_CURRENT, _CHANGED)

        mocks.encrypt.assert_not_called()
        mocks.write.assert_not_awaited()
