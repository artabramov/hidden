# tests/services/test_gocryptfs_init.py
# SPDX-License-Identifier: Apache-2.0

import unittest
from contextlib import contextmanager
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, call, patch

from app.constants import GOCRYPTFS_PASSPHRASE_LENGTH
from app.errors import BadGatewayError
from app.locks import lock_manager
from app.services.gocryptfs_init import gocryptfs_init

_PASSWORD = "пароль"
_PASSPHRASE = "секрет"


def _config():
    config = MagicMock()
    config.GOCRYPTFS_PASSPHRASE_PATH = "/secrets/passphrase"
    config.INSTALL_CIPHERDIR = "/cipher"
    config.VERSITY_ACCESS_KEY_PATH = "/secrets/access"
    config.VERSITY_SECRET_KEY_PATH = "/secrets/secret"
    return config


class TestGocryptfsInit(unittest.IsolatedAsyncioTestCase):
    def tearDown(self):
        self.assertFalse(lock_manager._lock.locked())

    @contextmanager
    def _patched(self):
        with (
            patch(
                "app.services.gocryptfs_init.get_config",
                return_value=_config(),
            ),
            patch(
                "app.services.gocryptfs_init.isfile",
                new=AsyncMock(return_value=False),
            ) as isfile,
            patch(
                "app.services.gocryptfs_init.is_cipherdir_created",
                new=AsyncMock(return_value=False),
            ) as cipherdir,
            patch(
                "app.services.gocryptfs_init.is_versity_created",
                new=AsyncMock(return_value=False),
            ) as versity,
            patch(
                "app.services.gocryptfs_init.generate_random_string",
                return_value=_PASSPHRASE,
            ) as generate,
            patch(
                "app.services.gocryptfs_init.encrypt_passphrase",
                return_value=b"encrypted",
            ) as encrypt,
            patch(
                "app.services.gocryptfs_init.write",
                new=AsyncMock(),
            ) as write,
            patch(
                "app.services.gocryptfs_init.cipherdir_create",
                new=AsyncMock(),
            ) as cipherdir_create,
            patch(
                "app.services.gocryptfs_init.versity_create",
                new=AsyncMock(return_value=("access-key", "secret-key")),
            ) as versity_create,
            patch(
                "app.services.gocryptfs_init.delete",
                new=AsyncMock(),
            ) as delete,
            patch("app.services.gocryptfs_init.log") as log,
        ):
            yield SimpleNamespace(
                isfile=isfile,
                cipherdir=cipherdir,
                versity=versity,
                generate=generate,
                encrypt=encrypt,
                write=write,
                cipherdir_create=cipherdir_create,
                versity_create=versity_create,
                delete=delete,
                log=log,
            )

    async def test_initializes_storage(self):
        async def absent(path):
            self.assertTrue(lock_manager._lock.locked())
            self.assertEqual(path, "/secrets/passphrase")
            return False

        with self._patched() as mocks:
            mocks.isfile.side_effect = absent
            result = await gocryptfs_init(_PASSWORD)

        self.assertEqual(result, ("access-key", "secret-key"))
        mocks.cipherdir.assert_awaited_once_with("/cipher")
        mocks.versity.assert_awaited_once_with(
            "/secrets/access",
            "/secrets/secret",
        )
        mocks.generate.assert_called_once_with(
            GOCRYPTFS_PASSPHRASE_LENGTH,
        )
        mocks.encrypt.assert_called_once_with(
            _PASSPHRASE.encode("utf-8"),
            _PASSWORD.encode("utf-8"),
        )
        mocks.write.assert_awaited_once_with(
            "/secrets/passphrase",
            b"encrypted",
        )
        mocks.cipherdir_create.assert_awaited_once_with(
            _PASSPHRASE,
            "/cipher",
        )
        mocks.versity_create.assert_awaited_once_with(
            "/secrets/access",
            "/secrets/secret",
        )
        mocks.delete.assert_not_awaited()
        mocks.log.warning.assert_not_called()

    async def test_rejects_existing_artifacts(self):
        cases = (
            (
                "passphrase",
                "isfile",
                "msg=gocryptfs_passphrase_already_exists",
                "cipherdir",
            ),
            (
                "cipherdir",
                "cipherdir",
                "msg=cipherdir_already_exists",
                "versity",
            ),
            (
                "versity",
                "versity",
                "msg=versity_already_exists",
                "generate",
            ),
        )

        for name, flag, message, skipped in cases:
            with self.subTest(existing=name):
                with self._patched() as mocks:
                    getattr(mocks, flag).return_value = True
                    with self.assertRaises(BadGatewayError):
                        await gocryptfs_init(_PASSWORD)

                mocks.log.warning.assert_called_once_with(message)
                mocks.delete.assert_not_awaited()
                if skipped == "generate":
                    mocks.generate.assert_not_called()
                else:
                    getattr(mocks, skipped).assert_not_awaited()

    async def test_leaves_storage_untouched_when_encryption_fails(self):
        with self._patched() as mocks:
            mocks.encrypt.side_effect = OSError("encrypt")
            with self.assertRaises(OSError):
                await gocryptfs_init(_PASSWORD)

        mocks.write.assert_not_awaited()
        mocks.delete.assert_not_awaited()
        mocks.log.exception.assert_not_called()

    async def test_removes_partial_artifacts_when_a_step_fails(self):
        failures = (
            ("write", "write"),
            ("cipherdir", "cipherdir_create"),
            ("versity", "versity_create"),
        )

        for name, target in failures:
            with self.subTest(step=name):
                with self._patched() as mocks:
                    getattr(mocks, target).side_effect = OSError(name)
                    with self.assertRaises(OSError) as caught:
                        await gocryptfs_init(_PASSWORD)

                self.assertEqual(str(caught.exception), name)
                mocks.log.exception.assert_called_once_with(
                    "msg=gocryptfs_initialization_failed",
                )
                self.assertEqual(
                    mocks.delete.await_args_list,
                    [
                        call("/secrets/passphrase"),
                        call("/cipher/gocryptfs.conf"),
                        call("/cipher/gocryptfs.diriv"),
                        call("/secrets/access"),
                        call("/secrets/secret"),
                    ],
                )
                if name == "write":
                    mocks.cipherdir_create.assert_not_awaited()
                if name != "versity":
                    mocks.versity_create.assert_not_awaited()
