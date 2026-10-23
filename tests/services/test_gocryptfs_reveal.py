# tests/services/test_gocryptfs_reveal.py
# SPDX-License-Identifier: Apache-2.0

import unittest
from contextlib import contextmanager
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

from app.errors import UnauthorizedError
from app.locks import lock_manager
from app.services.gocryptfs_reveal import gocryptfs_reveal

_PASSWORD = "пароль"
_PASSPHRASE = "секрет"


def _config():
    config = MagicMock()
    config.GOCRYPTFS_PASSPHRASE_PATH = "/secrets/passphrase"
    config.VERSITY_ACCESS_KEY_PATH = "/secrets/access"
    config.VERSITY_SECRET_KEY_PATH = "/secrets/secret"
    return config


class TestGocryptfsReveal(unittest.IsolatedAsyncioTestCase):
    def tearDown(self):
        self.assertFalse(lock_manager._lock.locked())

    @contextmanager
    def _patched(self):
        with (
            patch(
                "app.services.gocryptfs_reveal.get_config",
                return_value=_config(),
            ),
            patch(
                "app.services.gocryptfs_reveal.read",
                new=AsyncMock(
                    side_effect=[
                        b"encrypted",
                        b"access-key",
                        b"secret-key",
                    ],
                ),
            ) as read,
            patch(
                "app.services.gocryptfs_reveal.decrypt_passphrase",
                return_value=_PASSPHRASE.encode("utf-8"),
            ) as decrypt,
            patch("app.services.gocryptfs_reveal.log") as log,
        ):
            yield SimpleNamespace(read=read, decrypt=decrypt, log=log)

    async def test_returns_decrypted_secrets(self):
        reads = {
            "/secrets/passphrase": b"encrypted",
            "/secrets/access": "ключ".encode("utf-8"),
            "/secrets/secret": b"secret-key",
        }

        async def read_secret(path):
            self.assertTrue(lock_manager._lock.locked())
            return reads[path]

        with self._patched() as mocks:
            mocks.read.side_effect = read_secret
            result = await gocryptfs_reveal(_PASSWORD)

        self.assertEqual(
            result,
            (_PASSPHRASE, "ключ", "secret-key"),
        )
        mocks.decrypt.assert_called_once_with(
            b"encrypted",
            _PASSWORD.encode("utf-8"),
        )

    async def test_rejects_invalid_password(self):
        with self._patched() as mocks:
            mocks.decrypt.side_effect = ValueError("bad")
            with self.assertRaises(UnauthorizedError):
                await gocryptfs_reveal(_PASSWORD)

        mocks.log.warning.assert_called_once_with("msg=passphrase_invalid")
        self.assertEqual(mocks.read.await_count, 1)

    async def test_propagates_unexpected_decrypt_error(self):
        with self._patched() as mocks:
            mocks.decrypt.side_effect = OSError("decrypt")
            with self.assertRaises(OSError):
                await gocryptfs_reveal(_PASSWORD)

        mocks.log.warning.assert_not_called()
        self.assertEqual(mocks.read.await_count, 1)
