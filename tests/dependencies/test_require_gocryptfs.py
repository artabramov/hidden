# tests/dependencies/test_require_gocryptfs.py
# SPDX-License-Identifier: Apache-2.0

import unittest
from contextlib import contextmanager
from unittest.mock import AsyncMock, MagicMock, patch

from app.dependencies.require_gocryptfs import require_gocryptfs
from app.errors import BadGatewayError, ServiceUnavailableError

_LOGGER = "app.dependencies.require_gocryptfs"


class TestRequireGocryptfs(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.config = MagicMock()
        self.config.INSTALL_CIPHERDIR = "/cipherdir"
        self.config.INSTALL_MOUNTPOINT = "/mountpoint"
        self.config.GOCRYPTFS_PASSPHRASE_PATH = "/secrets/passphrase"

    @contextmanager
    def _patch_state(self, cipherdir, mountpoint, passphrase):
        cipherdir_mock = AsyncMock(return_value=cipherdir)
        mountpoint_mock = AsyncMock(return_value=mountpoint)
        passphrase_mock = AsyncMock(return_value=passphrase)

        with (
            patch(
                "app.dependencies.require_gocryptfs.get_config",
                return_value=self.config,
            ),
            patch(
                "app.dependencies.require_gocryptfs.is_cipherdir_created",
                cipherdir_mock,
            ),
            patch(
                "app.dependencies.require_gocryptfs.ismount",
                mountpoint_mock,
            ),
            patch(
                "app.dependencies.require_gocryptfs.isfile",
                passphrase_mock,
            ),
        ):
            yield cipherdir_mock, mountpoint_mock, passphrase_mock

    async def test_accepts_required_state_when_present(self):
        check = require_gocryptfs()

        with self._patch_state(True, True, True) as (
            cipherdir_mock,
            mountpoint_mock,
            passphrase_mock,
        ):
            await check()

        cipherdir_mock.assert_awaited_once_with("/cipherdir")
        mountpoint_mock.assert_awaited_once_with("/mountpoint")
        passphrase_mock.assert_awaited_once_with("/secrets/passphrase")

    async def test_accepts_forbidden_state_when_absent(self):
        check = require_gocryptfs(
            require_cipherdir=False,
            require_mountpoint=False,
            require_passphrase=False,
        )

        with self._patch_state(False, False, False) as (
            cipherdir_mock,
            mountpoint_mock,
            passphrase_mock,
        ):
            await check()

        cipherdir_mock.assert_awaited_once_with("/cipherdir")
        mountpoint_mock.assert_awaited_once_with("/mountpoint")
        passphrase_mock.assert_awaited_once_with("/secrets/passphrase")

    async def test_rejects_missing_required_cipherdir(self):
        check = require_gocryptfs()

        with self.assertLogs(_LOGGER, level="WARNING") as logs:
            with self._patch_state(False, True, True) as (
                cipherdir_mock,
                mountpoint_mock,
                passphrase_mock,
            ):
                with self.assertRaises(ServiceUnavailableError):
                    await check()

        cipherdir_mock.assert_awaited_once_with("/cipherdir")
        mountpoint_mock.assert_not_awaited()
        passphrase_mock.assert_not_awaited()
        self.assertIn("msg=cipherdir_not_found", logs.output[0])

    async def test_rejects_existing_forbidden_cipherdir(self):
        check = require_gocryptfs(require_cipherdir=False)

        with self.assertLogs(_LOGGER, level="WARNING") as logs:
            with self._patch_state(True, False, False) as (
                cipherdir_mock,
                mountpoint_mock,
                passphrase_mock,
            ):
                with self.assertRaises(BadGatewayError):
                    await check()

        cipherdir_mock.assert_awaited_once_with("/cipherdir")
        mountpoint_mock.assert_not_awaited()
        passphrase_mock.assert_not_awaited()
        self.assertIn("msg=cipherdir_exists", logs.output[0])

    async def test_rejects_missing_required_mountpoint(self):
        check = require_gocryptfs()

        with self.assertLogs(_LOGGER, level="WARNING") as logs:
            with self._patch_state(True, False, True) as (
                cipherdir_mock,
                mountpoint_mock,
                passphrase_mock,
            ):
                with self.assertRaises(ServiceUnavailableError):
                    await check()

        cipherdir_mock.assert_awaited_once_with("/cipherdir")
        mountpoint_mock.assert_awaited_once_with("/mountpoint")
        passphrase_mock.assert_not_awaited()
        self.assertIn("msg=mountpoint_not_found", logs.output[0])

    async def test_rejects_existing_forbidden_mountpoint(self):
        check = require_gocryptfs(require_mountpoint=False)

        with self.assertLogs(_LOGGER, level="WARNING") as logs:
            with self._patch_state(True, True, True) as (
                cipherdir_mock,
                mountpoint_mock,
                passphrase_mock,
            ):
                with self.assertRaises(BadGatewayError):
                    await check()

        cipherdir_mock.assert_awaited_once_with("/cipherdir")
        mountpoint_mock.assert_awaited_once_with("/mountpoint")
        passphrase_mock.assert_not_awaited()
        self.assertIn("msg=mountpoint_exists", logs.output[0])

    async def test_rejects_missing_required_passphrase(self):
        check = require_gocryptfs()

        with self.assertLogs(_LOGGER, level="WARNING") as logs:
            with self._patch_state(True, True, False) as (
                cipherdir_mock,
                mountpoint_mock,
                passphrase_mock,
            ):
                with self.assertRaises(ServiceUnavailableError):
                    await check()

        cipherdir_mock.assert_awaited_once_with("/cipherdir")
        mountpoint_mock.assert_awaited_once_with("/mountpoint")
        passphrase_mock.assert_awaited_once_with("/secrets/passphrase")
        self.assertIn("msg=passphrase_not_found", logs.output[0])

    async def test_rejects_existing_forbidden_passphrase(self):
        check = require_gocryptfs(require_passphrase=False)

        with self.assertLogs(_LOGGER, level="WARNING") as logs:
            with self._patch_state(True, True, True) as (
                cipherdir_mock,
                mountpoint_mock,
                passphrase_mock,
            ):
                with self.assertRaises(BadGatewayError):
                    await check()

        cipherdir_mock.assert_awaited_once_with("/cipherdir")
        mountpoint_mock.assert_awaited_once_with("/mountpoint")
        passphrase_mock.assert_awaited_once_with("/secrets/passphrase")
        self.assertIn("msg=passphrase_exists", logs.output[0])

    async def test_ignores_state_when_requirement_is_none(self):
        check = require_gocryptfs(
            require_cipherdir=None,
            require_mountpoint=None,
            require_passphrase=None,
        )

        with self.assertNoLogs(_LOGGER, level="WARNING"):
            with self._patch_state(True, True, True) as (
                cipherdir_mock,
                mountpoint_mock,
                passphrase_mock,
            ):
                await check()

        cipherdir_mock.assert_not_awaited()
        mountpoint_mock.assert_not_awaited()
        passphrase_mock.assert_not_awaited()
