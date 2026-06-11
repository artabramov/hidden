# tests/services/test_health_check.py
# SPDX-License-Identifier: GPL-3.0-only

import unittest
from datetime import datetime, timedelta, timezone, tzinfo
from unittest.mock import AsyncMock, MagicMock, patch
from zoneinfo import ZoneInfo

from app.constants import (
    LOCKDOWN_MODE_ENABLED_FLAG_PATH,
    WATCHDOG_HEARTBEAT_PATH,
)
from app.services.health_check import (
    _local_aware_now,
    _timezone_name,
    health_check,
)


class TestHealthCheck(unittest.IsolatedAsyncioTestCase):

    def _build_config(self):
        config = MagicMock()
        config.GOCRYPTFS_CIPHERDIR = "/fake/cipherdir"
        config.GOCRYPTFS_MOUNTPOINT = "/fake/mountpoint"
        config.FIRST_ADMIN_CREATED_FLAG_PATH = "/fake/secrets/first_admin_created.flag"  # noqa: E501
        config.GOCRYPTFS_WATCHDOG_LIVENESS_SECONDS = 10
        return config

    async def test_returns_health_snapshot_when_watchdog_alive(self):
        config = self._build_config()
        fixed_now = datetime(
            2026, 5, 3, 12, 0, 0,
            tzinfo=ZoneInfo("Europe/Amsterdam"),
        )

        watchdog_path = MagicMock()
        watchdog_path.is_file.return_value = True
        watchdog_path.stat.return_value.st_mtime = 100

        with (
            patch(
                "app.services.health_check.get_config",
                return_value=config,
            ),
            patch(
                "app.services.health_check.isfile",
                new=AsyncMock(side_effect=[True, True]),
            ) as isfile_mock,
            patch(
                "app.services.health_check.is_gocryptfs_initialized",
                new=AsyncMock(return_value=True),
            ) as initialized_mock,
            patch(
                "app.services.health_check.ismount",
                new=AsyncMock(return_value=True),
            ) as ismount_mock,
            patch(
                "app.services.health_check.Path",
                return_value=watchdog_path,
            ) as path_mock,
            patch("app.services.health_check.time.time", return_value=105),
            patch(
                "app.services.health_check._local_aware_now",
                return_value=fixed_now,
            ),
        ):
            result = await health_check()

        self.assertEqual(isfile_mock.await_count, 2)
        isfile_mock.assert_any_await(LOCKDOWN_MODE_ENABLED_FLAG_PATH)
        isfile_mock.assert_any_await(config.FIRST_ADMIN_CREATED_FLAG_PATH)
        initialized_mock.assert_awaited_once_with(config.GOCRYPTFS_CIPHERDIR)
        ismount_mock.assert_awaited_once_with(config.GOCRYPTFS_MOUNTPOINT)
        path_mock.assert_called_once_with(WATCHDOG_HEARTBEAT_PATH)
        watchdog_path.is_file.assert_called_once()
        watchdog_path.stat.assert_called_once()

        self.assertEqual(
            result,
            {
                "is_lockdown_mode_enabled": True,
                "is_first_admin_created": True,
                "is_cipherdir_created": True,
                "is_mountpoint_mounted": True,
                "is_watchdog_alive": True,
                "unix_timestamp": int(fixed_now.timestamp()),
                "timezone_name": "Europe/Amsterdam",
            },
        )

    async def test_returns_dead_watchdog_when_heartbeat_is_stale(self):
        config = self._build_config()
        fixed_now = datetime(2026, 5, 3, 12, 0, 0, tzinfo=timezone.utc)

        watchdog_path = MagicMock()
        watchdog_path.is_file.return_value = True
        watchdog_path.stat.return_value.st_mtime = 100

        with (
            patch(
                "app.services.health_check.get_config",
                return_value=config,
            ),
            patch(
                "app.services.health_check.isfile",
                new=AsyncMock(return_value=False),
            ),
            patch(
                "app.services.health_check.is_gocryptfs_initialized",
                new=AsyncMock(return_value=False),
            ),
            patch(
                "app.services.health_check.ismount",
                new=AsyncMock(return_value=False),
            ),
            patch(
                "app.services.health_check.Path",
                return_value=watchdog_path,
            ),
            patch("app.services.health_check.time.time", return_value=111),
            patch(
                "app.services.health_check._local_aware_now",
                return_value=fixed_now,
            ),
        ):
            result = await health_check()

        self.assertFalse(result["is_watchdog_alive"])
        self.assertFalse(result["is_lockdown_mode_enabled"])
        self.assertFalse(result["is_first_admin_created"])
        self.assertFalse(result["is_cipherdir_created"])
        self.assertFalse(result["is_mountpoint_mounted"])

    async def test_returns_dead_watchdog_when_heartbeat_file_missing(self):
        config = self._build_config()
        fixed_now = datetime(2026, 5, 3, 12, 0, 0, tzinfo=timezone.utc)

        watchdog_path = MagicMock()
        watchdog_path.is_file.return_value = False

        with (
            patch(
                "app.services.health_check.get_config",
                return_value=config,
            ),
            patch(
                "app.services.health_check.isfile",
                new=AsyncMock(return_value=False),
            ),
            patch(
                "app.services.health_check.is_gocryptfs_initialized",
                new=AsyncMock(return_value=True),
            ),
            patch(
                "app.services.health_check.ismount",
                new=AsyncMock(return_value=True),
            ),
            patch(
                "app.services.health_check.Path",
                return_value=watchdog_path,
            ),
            patch(
                "app.services.health_check._local_aware_now",
                return_value=fixed_now,
            ),
        ):
            result = await health_check()

        watchdog_path.is_file.assert_called_once()
        watchdog_path.stat.assert_not_called()
        self.assertFalse(result["is_watchdog_alive"])

    async def test_watchdog_is_alive_on_threshold_boundary(self):
        config = self._build_config()
        fixed_now = datetime(2026, 5, 3, 12, 0, 0, tzinfo=timezone.utc)

        watchdog_path = MagicMock()
        watchdog_path.is_file.return_value = True
        watchdog_path.stat.return_value.st_mtime = 100

        with (
            patch(
                "app.services.health_check.get_config",
                return_value=config,
            ),
            patch(
                "app.services.health_check.isfile",
                new=AsyncMock(return_value=False),
            ),
            patch(
                "app.services.health_check.is_gocryptfs_initialized",
                new=AsyncMock(return_value=False),
            ),
            patch(
                "app.services.health_check.ismount",
                new=AsyncMock(return_value=False),
            ),
            patch(
                "app.services.health_check.Path",
                return_value=watchdog_path,
            ),
            patch("app.services.health_check.time.time", return_value=110),
            patch(
                "app.services.health_check._local_aware_now",
                return_value=fixed_now,
            ),
        ):
            result = await health_check()

        self.assertTrue(result["is_watchdog_alive"])


class TestLocalAwareNow(unittest.TestCase):

    def test_returns_timezone_aware_datetime(self):
        now = _local_aware_now()

        self.assertIsInstance(now, datetime)
        self.assertIsNotNone(now.tzinfo)
        self.assertIsNotNone(now.utcoffset())


class TestTimezoneName(unittest.TestCase):

    def test_returns_iana_timezone_name_when_available(self):
        now = datetime(
            2026, 5, 3, 12, 0, 0,
            tzinfo=ZoneInfo("Europe/Amsterdam"),
        )

        self.assertEqual(_timezone_name(now), "Europe/Amsterdam")

    def test_returns_tzname_when_iana_key_is_missing(self):
        now = datetime(
            2026, 5, 3, 12, 0, 0,
            tzinfo=timezone(timedelta(hours=3), "MSK"),
        )

        self.assertEqual(_timezone_name(now), "MSK")

    def test_returns_utc_when_datetime_is_naive(self):
        now = datetime(2026, 5, 3, 12, 0, 0)

        self.assertEqual(_timezone_name(now), "UTC")

    def test_returns_local_when_timezone_has_no_label(self):
        class NamelessTimezone(tzinfo):
            def utcoffset(self, dt):
                return timedelta(hours=1)

            def dst(self, dt):
                return timedelta(0)

            def tzname(self, dt):
                return None

        now = datetime(2026, 5, 3, 12, 0, 0, tzinfo=NamelessTimezone())
        self.assertEqual(_timezone_name(now), "local")
