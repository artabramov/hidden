# tests/runtime/test_watchdog.py
# SPDX-License-Identifier: Apache-2.0

import runpy
import unittest
from contextlib import contextmanager
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

from app.constants import WATCHDOG_HEARTBEAT_PATH
from app.runtime import watchdog
from app.runtime.watchdog import (
    _emergency_unmount,
    _is_application_running,
    run_watchdog,
)


def _entry(name, payload=b"", error=None):
    entry = MagicMock()
    entry.name = name
    cmdline = MagicMock()
    if error is None:
        cmdline.read_bytes.return_value = payload
    else:
        cmdline.read_bytes.side_effect = error
    entry.__truediv__.return_value = cmdline
    return entry


class TestRunWatchdog(unittest.IsolatedAsyncioTestCase):
    @contextmanager
    def _patched(
        self,
        *,
        mounted,
        exists=True,
        size=4,
        isfile_error=None,
        size_error=None,
        running=True,
    ):
        config = MagicMock()
        config.INSTALL_MOUNTPOINT = "/mountpoint"
        config.GOCRYPTFS_PASSPHRASE_PATH = "/secrets/passphrase"
        isfile = MagicMock(return_value=exists)
        if isfile_error is not None:
            isfile.side_effect = isfile_error
        getsize = MagicMock(return_value=size)
        if size_error is not None:
            getsize.side_effect = size_error

        with (
            patch(
                "app.runtime.watchdog.get_config",
                return_value=config,
            ),
            patch("app.runtime.watchdog.Path") as path,
            patch(
                "app.runtime.watchdog.ismount",
                new=AsyncMock(return_value=mounted),
            ) as ismount,
            patch("app.runtime.watchdog.os.path.isfile", new=isfile),
            patch("app.runtime.watchdog.os.path.getsize", new=getsize),
            patch(
                "app.runtime.watchdog._is_application_running",
                return_value=running,
            ) as application,
            patch(
                "app.runtime.watchdog._emergency_unmount",
                new=AsyncMock(),
            ) as unmount,
            patch(
                "app.runtime.watchdog.versity_stop",
                new=AsyncMock(),
            ) as stop,
            patch("app.runtime.watchdog.log") as log,
        ):
            yield SimpleNamespace(
                path=path,
                ismount=ismount,
                isfile=isfile,
                getsize=getsize,
                application=application,
                unmount=unmount,
                stop=stop,
                log=log,
            )

    def _assert_heartbeat(self, mocks):
        mocks.path.assert_called_once_with(WATCHDOG_HEARTBEAT_PATH)
        mocks.path.return_value.touch.assert_called_once_with()

    async def test_stops_versity_when_mountpoint_is_absent(self):
        with self._patched(mounted=False) as mocks:
            await run_watchdog()

        self._assert_heartbeat(mocks)
        mocks.ismount.assert_awaited_once_with("/mountpoint")
        mocks.stop.assert_awaited_once_with()
        mocks.isfile.assert_not_called()
        mocks.application.assert_not_called()
        mocks.unmount.assert_not_awaited()

    async def test_keeps_mount_when_storage_is_healthy(self):
        with self._patched(mounted=True) as mocks:
            await run_watchdog()

        self._assert_heartbeat(mocks)
        mocks.isfile.assert_called_once_with("/secrets/passphrase")
        mocks.getsize.assert_called_once_with("/secrets/passphrase")
        mocks.application.assert_called_once_with()
        mocks.stop.assert_not_awaited()
        mocks.unmount.assert_not_awaited()
        mocks.log.warning.assert_not_called()

    async def test_unmounts_when_passphrase_file_is_missing(self):
        with self._patched(mounted=True, exists=False) as mocks:
            await run_watchdog()

        mocks.getsize.assert_not_called()
        mocks.application.assert_not_called()
        mocks.log.warning.assert_called_once_with(
            "msg=watchdog_passphrase_missing",
        )
        mocks.unmount.assert_awaited_once_with("/mountpoint")

    async def test_unmounts_when_passphrase_file_is_empty(self):
        with self._patched(mounted=True, size=0) as mocks:
            await run_watchdog()

        mocks.unmount.assert_awaited_once_with("/mountpoint")
        mocks.log.warning.assert_called_once_with(
            "msg=watchdog_passphrase_missing",
        )

    async def test_unmounts_when_passphrase_stat_fails(self):
        cases = (
            ("isfile", OSError("gone"), None),
            ("getsize", None, OSError("gone")),
        )

        for name, isfile_error, size_error in cases:
            with self.subTest(source=name):
                with self._patched(
                    mounted=True,
                    isfile_error=isfile_error,
                    size_error=size_error,
                ) as mocks:
                    await run_watchdog()

                mocks.unmount.assert_awaited_once_with("/mountpoint")
                if isfile_error is not None:
                    mocks.getsize.assert_not_called()

    async def test_unmounts_when_application_is_missing(self):
        with self._patched(mounted=True, running=False) as mocks:
            await run_watchdog()

        mocks.log.warning.assert_called_once_with(
            "msg=watchdog_application_missing",
        )
        mocks.unmount.assert_awaited_once_with("/mountpoint")
        mocks.stop.assert_not_awaited()


class TestIsApplicationRunning(unittest.TestCase):
    def test_returns_false_when_proc_cannot_be_listed(self):
        proc = MagicMock()
        proc.iterdir.side_effect = OSError("proc")

        with patch("app.runtime.watchdog.Path", return_value=proc) as path:
            running = _is_application_running()

        self.assertIs(running, False)
        path.assert_called_once_with("/proc")

    def test_finds_uvicorn_application(self):
        skipped = _entry("cpu")
        unreadable = _entry("8", error=OSError("cmdline"))
        empty = _entry("9", payload=b"")
        other = _entry("10", payload=b"uvicorn\x00other")
        match = _entry("11", payload=b"uvicorn\x00app.main:app\x00")
        later = _entry("12", payload=b"uvicorn\x00app.main:app\x00")
        proc = MagicMock()
        proc.iterdir.return_value = [
            skipped,
            unreadable,
            empty,
            other,
            match,
            later,
        ]

        with patch("app.runtime.watchdog.Path", return_value=proc):
            running = _is_application_running()

        self.assertIs(running, True)
        skipped.__truediv__.assert_not_called()
        later.__truediv__.assert_not_called()

    def test_returns_false_without_both_markers(self):
        proc = MagicMock()
        proc.iterdir.return_value = [
            _entry("3", payload=b"uvicorn"),
            _entry("4", payload=b"app.main:app"),
        ]

        with patch("app.runtime.watchdog.Path", return_value=proc):
            running = _is_application_running()

        self.assertIs(running, False)


class TestEmergencyUnmount(unittest.IsolatedAsyncioTestCase):
    async def test_stops_versity_and_unmounts(self):
        with (
            patch(
                "app.runtime.watchdog.versity_stop",
                new=AsyncMock(),
            ) as stop,
            patch(
                "app.runtime.watchdog.cipherdir_unmount",
                new=AsyncMock(),
            ) as unmount,
            patch("app.runtime.watchdog.log") as log,
        ):
            await _emergency_unmount("/mountpoint")

        stop.assert_awaited_once_with()
        unmount.assert_awaited_once_with("/mountpoint")
        log.info.assert_called_once_with("msg=watchdog_unmount_completed")

    async def test_unmounts_when_versity_stop_fails(self):
        with (
            patch(
                "app.runtime.watchdog.versity_stop",
                new=AsyncMock(side_effect=RuntimeError("stop")),
            ),
            patch(
                "app.runtime.watchdog.cipherdir_unmount",
                new=AsyncMock(),
            ) as unmount,
            patch("app.runtime.watchdog.log") as log,
        ):
            await _emergency_unmount("/mountpoint")

        unmount.assert_awaited_once_with("/mountpoint")
        log.info.assert_called_once_with("msg=watchdog_unmount_completed")


class TestWatchdogMain(unittest.TestCase):
    def test_runs_watchdog_and_exits(self):
        def finish(coro):
            try:
                self.assertEqual(coro.cr_code.co_name, "run_watchdog")
            finally:
                coro.close()
            return 0

        with (
            patch("app.log.init_logging") as init_logging,
            patch("asyncio.run", side_effect=finish) as run,
        ):
            with self.assertRaises(SystemExit) as raised:
                runpy.run_path(
                    watchdog.__file__,
                    run_name="__main__",
                )

        self.assertEqual(raised.exception.code, 0)
        init_logging.assert_called_once_with()
        run.assert_called_once()
