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
                new=AsyncMock(return_value=b"encrypted"),
            ) as read,
            patch(
                "app.services.gocryptfs_reveal.decrypt_passphrase",
                return_value=_PASSPHRASE.encode("utf-8"),
            ) as decrypt,
            patch(
                "app.services.gocryptfs_reveal.versity_read",
                new=AsyncMock(return_value=("ключ", "secret-key")),
            ) as versity_read,
            patch("app.services.gocryptfs_reveal.log") as log,
        ):
            yield SimpleNamespace(
                read=read,
                decrypt=decrypt,
                versity_read=versity_read,
                log=log,
            )

    async def test_returns_decrypted_secrets(self):
        async def read_credentials(access_path, secret_path, passphrase):
            self.assertTrue(lock_manager._lock.locked())
            return "ключ", "secret-key"

        with self._patched() as mocks:
            mocks.versity_read.side_effect = read_credentials
            result = await gocryptfs_reveal(_PASSWORD)

        self.assertEqual(
            result,
            (_PASSPHRASE, "ключ", "secret-key"),
        )
        mocks.read.assert_awaited_once_with("/secrets/passphrase")
        mocks.decrypt.assert_called_once_with(
            b"encrypted",
            _PASSWORD.encode("utf-8"),
        )
        mocks.versity_read.assert_awaited_once_with(
            "/secrets/access",
            "/secrets/secret",
            _PASSPHRASE,
        )

    async def test_rejects_invalid_password(self):
        with self._patched() as mocks:
            mocks.decrypt.side_effect = ValueError("bad")
            with self.assertRaises(UnauthorizedError):
                await gocryptfs_reveal(_PASSWORD)

        mocks.log.warning.assert_called_once_with("msg=passphrase_invalid")
        mocks.versity_read.assert_not_awaited()

    async def test_propagates_unexpected_decrypt_error(self):
        with self._patched() as mocks:
            mocks.decrypt.side_effect = OSError("decrypt")
            with self.assertRaises(OSError):
                await gocryptfs_reveal(_PASSWORD)

        mocks.log.warning.assert_not_called()
        mocks.versity_read.assert_not_awaited()

    async def test_propagates_credential_decrypt_error(self):
        with self._patched() as mocks:
            mocks.versity_read.side_effect = ValueError("corrupted")
            with self.assertRaises(ValueError):
                await gocryptfs_reveal(_PASSWORD)

        mocks.log.warning.assert_not_called()
