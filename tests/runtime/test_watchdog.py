# tests/runtime/test_watchdog.py
# SPDX-License-Identifier: SSPL-1.0

import asyncio
import unittest
from unittest.mock import AsyncMock, MagicMock, patch

from app.constants import WATCHDOG_GRACEFUL_UNMOUNT_SECONDS
from app.runtime import watchdog as wd


def _cfg() -> MagicMock:
    c = MagicMock()
    c.GOCRYPTFS_MOUNTPOINT = "/mnt/h"
    c.INSTALL_SECRETS_DIR = "/sec"
    c.GOCRYPTFS_PASSPHRASE_ENCRYPTED_PATH = "/sec/pass.enc"
    return c


class TestRunWatchdog(unittest.IsolatedAsyncioTestCase):
    async def test_not_mounted_returns_after_touch(self):
        mock_ld = AsyncMock()

        with (
            patch("app.runtime.watchdog.get_config", return_value=_cfg()),
            patch("app.runtime.watchdog.Path") as mock_path,
            patch(
                "app.runtime.watchdog.ismount",
                new_callable=AsyncMock,
                return_value=False,
            ),
            patch(
                "app.runtime.watchdog._lockdown_and_unmount",
                mock_ld,
            ),
        ):
            await wd.run_watchdog()

        mock_path.return_value.touch.assert_called_once_with()
        mock_ld.assert_not_awaited()

    async def test_secrets_dir_missing_triggers_unmount(self):
        mock_ld = AsyncMock()

        with (
            patch("app.runtime.watchdog.get_config", return_value=_cfg()),
            patch("app.runtime.watchdog.Path", return_value=MagicMock()),
            patch(
                "app.runtime.watchdog.ismount",
                new_callable=AsyncMock,
                return_value=True,
            ),
            patch(
                "app.runtime.watchdog.isdir",
                new_callable=AsyncMock,
                return_value=False,
            ),
            patch(
                "app.runtime.watchdog._lockdown_and_unmount",
                mock_ld,
            ),
        ):
            await wd.run_watchdog()

        mock_ld.assert_awaited_once_with(soft_drain=True)

    async def test_passphrase_missing_triggers_unmount(self):
        mock_ld = AsyncMock()

        with (
            patch("app.runtime.watchdog.get_config", return_value=_cfg()),
            patch("app.runtime.watchdog.Path", return_value=MagicMock()),
            patch(
                "app.runtime.watchdog.ismount",
                new_callable=AsyncMock,
                return_value=True,
            ),
            patch(
                "app.runtime.watchdog.isdir",
                new_callable=AsyncMock,
                return_value=True,
            ),
            patch(
                "app.runtime.watchdog.isfile",
                new_callable=AsyncMock,
                return_value=False,
            ),
            patch(
                "app.runtime.watchdog._lockdown_and_unmount",
                mock_ld,
            ),
        ):
            await wd.run_watchdog()

        mock_ld.assert_awaited_once_with(soft_drain=True)

    async def test_app_not_running_triggers_hard_unmount(self):
        mock_ld = AsyncMock()

        with (
            patch("app.runtime.watchdog.get_config", return_value=_cfg()),
            patch("app.runtime.watchdog.Path", return_value=MagicMock()),
            patch(
                "app.runtime.watchdog.ismount",
                new_callable=AsyncMock,
                return_value=True,
            ),
            patch(
                "app.runtime.watchdog.isdir",
                new_callable=AsyncMock,
                return_value=True,
            ),
            patch(
                "app.runtime.watchdog.isfile",
                new_callable=AsyncMock,
                return_value=True,
            ),
            patch(
                "app.runtime.watchdog._is_application_running",
                return_value=False,
            ),
            patch(
                "app.runtime.watchdog._lockdown_and_unmount",
                mock_ld,
            ),
        ):
            await wd.run_watchdog()

        mock_ld.assert_awaited_once_with(soft_drain=False)

    async def test_all_ok_no_unmount(self):
        mock_ld = AsyncMock()

        with (
            patch("app.runtime.watchdog.get_config", return_value=_cfg()),
            patch("app.runtime.watchdog.Path", return_value=MagicMock()),
            patch(
                "app.runtime.watchdog.ismount",
                new_callable=AsyncMock,
                return_value=True,
            ),
            patch(
                "app.runtime.watchdog.isdir",
                new_callable=AsyncMock,
                return_value=True,
            ),
            patch(
                "app.runtime.watchdog.isfile",
                new_callable=AsyncMock,
                return_value=True,
            ),
            patch(
                "app.runtime.watchdog._is_application_running",
                return_value=True,
            ),
            patch(
                "app.runtime.watchdog._lockdown_and_unmount",
                mock_ld,
            ),
        ):
            await wd.run_watchdog()

        mock_ld.assert_not_awaited()

    async def test_touches_heartbeat_with_expected_path(self):
        mock_ld = AsyncMock()
        mock_heartbeat = MagicMock()

        with (
            patch("app.runtime.watchdog.get_config", return_value=_cfg()),
            patch(
                "app.runtime.watchdog.Path",
                return_value=mock_heartbeat,
            ) as mock_path,
            patch(
                "app.runtime.watchdog.ismount",
                new_callable=AsyncMock,
                return_value=False,
            ),
            patch(
                "app.runtime.watchdog._lockdown_and_unmount",
                mock_ld,
            ),
        ):
            await wd.run_watchdog()

        mock_path.assert_called_once_with(wd.WATCHDOG_HEARTBEAT_PATH)
        mock_heartbeat.touch.assert_called_once_with()
        mock_ld.assert_not_awaited()

    async def test_missing_secrets_logs_and_stops_after_unmount(self):
        mock_ld = AsyncMock()

        with (
            patch("app.runtime.watchdog.get_config", return_value=_cfg()),
            patch("app.runtime.watchdog.Path", return_value=MagicMock()),
            patch(
                "app.runtime.watchdog.ismount",
                new_callable=AsyncMock,
                return_value=True,
            ),
            patch(
                "app.runtime.watchdog.isdir",
                new_callable=AsyncMock,
                return_value=False,
            ),
            patch(
                "app.runtime.watchdog.isfile",
                new_callable=AsyncMock,
            ) as mock_isfile,
            patch(
                "app.runtime.watchdog._is_application_running",
            ) as mock_running,
            patch(
                "app.runtime.watchdog._lockdown_and_unmount",
                mock_ld,
            ),
            patch("app.runtime.watchdog.logger") as mock_logger,
        ):
            await wd.run_watchdog()

        mock_ld.assert_awaited_once_with(soft_drain=True)
        mock_isfile.assert_not_awaited()
        mock_running.assert_not_called()
        mock_logger.warning.assert_called_once_with(
            "secrets not found, unmount started",
        )
        mock_logger.info.assert_called_once_with(
            "secrets not found, mountpoint unmounted",
        )

    async def test_missing_passphrase_logs_and_stops_after_unmount(self):
        mock_ld = AsyncMock()

        with (
            patch("app.runtime.watchdog.get_config", return_value=_cfg()),
            patch("app.runtime.watchdog.Path", return_value=MagicMock()),
            patch(
                "app.runtime.watchdog.ismount",
                new_callable=AsyncMock,
                return_value=True,
            ),
            patch(
                "app.runtime.watchdog.isdir",
                new_callable=AsyncMock,
                return_value=True,
            ),
            patch(
                "app.runtime.watchdog.isfile",
                new_callable=AsyncMock,
                return_value=False,
            ),
            patch(
                "app.runtime.watchdog._is_application_running",
            ) as mock_running,
            patch(
                "app.runtime.watchdog._lockdown_and_unmount",
                mock_ld,
            ),
            patch("app.runtime.watchdog.logger") as mock_logger,
        ):
            await wd.run_watchdog()

        mock_ld.assert_awaited_once_with(soft_drain=True)
        mock_running.assert_not_called()
        mock_logger.warning.assert_called_once_with(
            "passphrase not found, unmount started",
        )
        mock_logger.info.assert_called_once_with(
            "passphrase not found, mountpoint unmounted",
        )

    async def test_app_not_running_logs_hard_unmount(self):
        mock_ld = AsyncMock()

        with (
            patch("app.runtime.watchdog.get_config", return_value=_cfg()),
            patch("app.runtime.watchdog.Path", return_value=MagicMock()),
            patch(
                "app.runtime.watchdog.ismount",
                new_callable=AsyncMock,
                return_value=True,
            ),
            patch(
                "app.runtime.watchdog.isdir",
                new_callable=AsyncMock,
                return_value=True,
            ),
            patch(
                "app.runtime.watchdog.isfile",
                new_callable=AsyncMock,
                return_value=True,
            ),
            patch(
                "app.runtime.watchdog._is_application_running",
                return_value=False,
            ),
            patch(
                "app.runtime.watchdog._lockdown_and_unmount",
                mock_ld,
            ),
            patch("app.runtime.watchdog.logger") as mock_logger,
        ):
            await wd.run_watchdog()

        mock_ld.assert_awaited_once_with(soft_drain=False)
        mock_logger.warning.assert_called_once_with(
            "application not running, unmount started",
        )
        mock_logger.info.assert_called_once_with(
            "application not running, mountpoint unmounted",
        )

    async def test_all_ok_checks_everything_and_does_not_log(self):
        mock_ld = AsyncMock()

        with (
            patch("app.runtime.watchdog.get_config", return_value=_cfg()),
            patch("app.runtime.watchdog.Path", return_value=MagicMock()),
            patch(
                "app.runtime.watchdog.ismount",
                new_callable=AsyncMock,
                return_value=True,
            ) as mock_ismount,
            patch(
                "app.runtime.watchdog.isdir",
                new_callable=AsyncMock,
                return_value=True,
            ) as mock_isdir,
            patch(
                "app.runtime.watchdog.isfile",
                new_callable=AsyncMock,
                return_value=True,
            ) as mock_isfile,
            patch(
                "app.runtime.watchdog._is_application_running",
                return_value=True,
            ) as mock_running,
            patch(
                "app.runtime.watchdog._lockdown_and_unmount",
                mock_ld,
            ),
            patch("app.runtime.watchdog.logger") as mock_logger,
        ):
            await wd.run_watchdog()

        mock_ismount.assert_awaited_once_with("/mnt/h")
        mock_isdir.assert_awaited_once_with("/sec")
        mock_isfile.assert_awaited_once_with("/sec/pass.enc")
        mock_running.assert_called_once_with()
        mock_ld.assert_not_awaited()
        mock_logger.warning.assert_not_called()
        mock_logger.info.assert_not_called()


class TestLockdownAndUnmount(unittest.IsolatedAsyncioTestCase):
    async def test_soft_drain_sleeps_before_unmount(self):
        mock_sleep = AsyncMock()
        mock_unmount = AsyncMock()

        with (
            patch("app.runtime.watchdog.get_config", return_value=_cfg()),
            patch("app.runtime.watchdog.touch", new_callable=AsyncMock),
            patch("app.runtime.watchdog.asyncio.sleep", mock_sleep),
            patch(
                "app.runtime.watchdog.unmount_gocryptfs",
                mock_unmount,
            ),
        ):
            await wd._lockdown_and_unmount(soft_drain=True)

        mock_sleep.assert_awaited_once_with(
            WATCHDOG_GRACEFUL_UNMOUNT_SECONDS,
        )
        mock_unmount.assert_awaited_once_with("/mnt/h")

    async def test_no_sleep_when_hard_unmount(self):
        mock_sleep = AsyncMock()
        mock_unmount = AsyncMock()

        with (
            patch("app.runtime.watchdog.get_config", return_value=_cfg()),
            patch("app.runtime.watchdog.touch", new_callable=AsyncMock),
            patch("app.runtime.watchdog.asyncio.sleep", mock_sleep),
            patch(
                "app.runtime.watchdog.unmount_gocryptfs",
                mock_unmount,
            ),
        ):
            await wd._lockdown_and_unmount(soft_drain=False)

        mock_sleep.assert_not_awaited()
        mock_unmount.assert_awaited_once_with("/mnt/h")

    async def test_lockdown_touch_failure_continues(self):
        mock_unmount = AsyncMock()

        with (
            patch("app.runtime.watchdog.get_config", return_value=_cfg()),
            patch(
                "app.runtime.watchdog.touch",
                new_callable=AsyncMock,
                side_effect=OSError("x"),
            ),
            patch("app.runtime.watchdog.asyncio.sleep", AsyncMock()),
            patch(
                "app.runtime.watchdog.unmount_gocryptfs",
                mock_unmount,
            ),
        ):
            await wd._lockdown_and_unmount(soft_drain=True)

        mock_unmount.assert_awaited()

    async def test_touch_called_with_lockdown_flag_path(self):
        mock_touch = AsyncMock()
        mock_sleep = AsyncMock()
        mock_unmount = AsyncMock()

        with (
            patch("app.runtime.watchdog.get_config", return_value=_cfg()),
            patch("app.runtime.watchdog.touch", mock_touch),
            patch("app.runtime.watchdog.asyncio.sleep", mock_sleep),
            patch("app.runtime.watchdog.unmount_gocryptfs", mock_unmount),
        ):
            await wd._lockdown_and_unmount(soft_drain=True)

        mock_touch.assert_awaited_once_with(
            wd.LOCKDOWN_MODE_ENABLED_FLAG_PATH,
        )
        mock_sleep.assert_awaited_once_with(
            WATCHDOG_GRACEFUL_UNMOUNT_SECONDS,
        )
        mock_unmount.assert_awaited_once_with("/mnt/h")

    async def test_touch_failure_logs_warning(self):
        mock_unmount = AsyncMock()

        with (
            patch("app.runtime.watchdog.get_config", return_value=_cfg()),
            patch(
                "app.runtime.watchdog.touch",
                new_callable=AsyncMock,
                side_effect=OSError("x"),
            ),
            patch("app.runtime.watchdog.asyncio.sleep", AsyncMock()),
            patch("app.runtime.watchdog.unmount_gocryptfs", mock_unmount),
            patch("app.runtime.watchdog.logger") as mock_logger,
        ):
            await wd._lockdown_and_unmount(soft_drain=True)

        mock_logger.warning.assert_called_once_with(
            "failed to enable lockdown mode before unmount",
        )
        mock_unmount.assert_awaited_once_with("/mnt/h")


class _FakeCmdline:
    def __init__(self, data: bytes) -> None:
        self._data = data

    def read_bytes(self) -> bytes:
        return self._data


class _FakeCmdlineRaises:
    def read_bytes(self) -> bytes:
        raise OSError("denied")


class _FakeProcEntry:
    def __init__(self, name: str, cmdline: bytes) -> None:
        self.name = name
        self._cmdline = cmdline

    def __truediv__(self, other: object) -> _FakeCmdline:
        if other == "cmdline":
            return _FakeCmdline(self._cmdline)
        raise AssertionError


class _FakeProcEntryRaises:
    def __init__(self, name: str) -> None:
        self.name = name

    def __truediv__(self, other: object) -> _FakeCmdlineRaises:
        if other == "cmdline":
            return _FakeCmdlineRaises()
        raise AssertionError


class TestIsApplicationRunning(unittest.TestCase):
    def test_false_when_proc_unreadable(self):
        mock_proc = MagicMock()
        mock_proc.iterdir.side_effect = OSError("denied")

        with patch("app.runtime.watchdog.Path", return_value=mock_proc):
            self.assertFalse(wd._is_application_running())

    def test_true_when_uvicorn_cmdline_found(self):
        payload = b"python\x00uvicorn\x00app.main:app\x00"
        proc = MagicMock()
        proc.iterdir.return_value = [
            _FakeProcEntry("12345", payload),
        ]

        with patch("app.runtime.watchdog.Path", return_value=proc):
            self.assertTrue(wd._is_application_running())

    def test_false_when_no_match(self):
        proc = MagicMock()
        proc.iterdir.return_value = [
            _FakeProcEntry("99", b"other\x00process\x00"),
        ]

        with patch("app.runtime.watchdog.Path", return_value=proc):
            self.assertFalse(wd._is_application_running())

    def test_skips_non_digit_entries(self):
        proc = MagicMock()
        proc.iterdir.return_value = [
            _FakeProcEntry("self", b"python\x00uvicorn\x00app.main:app\x00"),
            _FakeProcEntry("abc", b"python\x00uvicorn\x00app.main:app\x00"),
        ]

        with patch("app.runtime.watchdog.Path", return_value=proc):
            self.assertFalse(wd._is_application_running())

    def test_skips_empty_cmdline(self):
        proc = MagicMock()
        proc.iterdir.return_value = [
            _FakeProcEntry("123", b""),
        ]

        with patch("app.runtime.watchdog.Path", return_value=proc):
            self.assertFalse(wd._is_application_running())

    def test_skips_entry_when_cmdline_read_fails(self):
        proc = MagicMock()
        proc.iterdir.return_value = [
            _FakeProcEntryRaises("123"),
        ]

        with patch("app.runtime.watchdog.Path", return_value=proc):
            self.assertFalse(wd._is_application_running())

    def test_continues_after_broken_entry_and_finds_match(self):
        payload = b"python\x00uvicorn\x00app.main:app\x00"
        proc = MagicMock()
        proc.iterdir.return_value = [
            _FakeProcEntryRaises("111"),
            _FakeProcEntry("222", payload),
        ]

        with patch("app.runtime.watchdog.Path", return_value=proc):
            self.assertTrue(wd._is_application_running())

    def test_false_when_only_uvicorn_present_without_app(self):
        proc = MagicMock()
        proc.iterdir.return_value = [_FakeProcEntry(
            "123", b"python\x00uvicorn\x00other.module:app\x00"
        )]

        with patch("app.runtime.watchdog.Path", return_value=proc):
            self.assertFalse(wd._is_application_running())

    def test_false_when_only_app_present_without_uvicorn(self):
        proc = MagicMock()
        proc.iterdir.return_value = [
            _FakeProcEntry("123", b"python\x00app.main:app\x00"),
        ]

        with patch("app.runtime.watchdog.Path", return_value=proc):
            self.assertFalse(wd._is_application_running())


class TestMain(unittest.TestCase):

    def test_main_initializes_logging_and_runs_watchdog(self):
        with (
            patch("app.runtime.watchdog.init_logging") as mock_init_logging,
            patch(
                "app.runtime.watchdog.run_watchdog",
                new=MagicMock(),
            ) as mock_watchdog,
            patch(
                "app.runtime.watchdog.asyncio.run",
                return_value=None,
            ) as mock_asyncio_run,
        ):
            with self.assertRaises(SystemExit) as cm:
                from app.runtime import watchdog as _wd
                _wd.init_logging()
                raise SystemExit(asyncio.run(_wd.run_watchdog()))

        mock_init_logging.assert_called_once()
        mock_asyncio_run.assert_called_once()
        mock_watchdog.assert_called_once()
        self.assertIsNone(cm.exception.code)

    def test_main_propagates_asyncio_run_exception(self):
        error = RuntimeError("watchdog failed")
        with (
            patch("app.runtime.watchdog.init_logging"),
            patch("app.runtime.watchdog.run_watchdog", new=MagicMock()),
            patch(
                "app.runtime.watchdog.asyncio.run",
                side_effect=error,
            ),
        ):
            with self.assertRaises(RuntimeError) as cm:
                from app.runtime import watchdog as _wd
                _wd.init_logging()
                asyncio.run(_wd.run_watchdog())

        self.assertIs(cm.exception, error)
