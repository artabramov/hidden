# tests/services/test_gocryptfs_health.py
# SPDX-License-Identifier: Apache-2.0

import unittest
from datetime import datetime, timedelta, tzinfo
from unittest.mock import AsyncMock, MagicMock, patch

from app.constants import WATCHDOG_HEARTBEAT_PATH
from app.services.gocryptfs_health import (
    _local_aware_now,
    _timezone_name,
    gocryptfs_health,
)


class _Zone(tzinfo):
    key = "Asia/Tbilisi"

    def utcoffset(self, dt):
        return timedelta(0)

    def dst(self, dt):
        return timedelta(0)

    def tzname(self, dt):
        return "GET"


_MOMENT = datetime(2026, 10, 23, 5, 0, tzinfo=_Zone())


def _config():
    config = MagicMock()
    config.INSTALL_CIPHERDIR = "/cipher"
    config.INSTALL_MOUNTPOINT = "/mount"
    config.VERSITY_ACCESS_KEY_PATH = "/secrets/access"
    config.VERSITY_SECRET_KEY_PATH = "/secrets/secret"
    config.WATCHDOG_LIVENESS_SECONDS = 30
    return config


class TestGocryptfsHealth(unittest.IsolatedAsyncioTestCase):
    async def test_reports_runtime_status(self):
        cases = (
            ("missing", False, None, False),
            ("fresh", True, 970.0, True),
            ("stale", True, 969.0, False),
        )
        flags = {
            "is_cipherdir_created": True,
            "is_cipherdir_mounted": False,
            "is_versity_created": False,
            "is_versity_running": True,
        }

        for name, exists, mtime, alive in cases:
            with self.subTest(heartbeat=name):
                result = await self._health(exists, mtime, flags)
                self.assertEqual(
                    result,
                    {
                        **flags,
                        "is_watchdog_alive": alive,
                        "unix_timestamp": int(_MOMENT.timestamp()),
                        "timezone_name": "Asia/Tbilisi",
                    },
                )

    async def _health(self, exists, mtime, flags):
        heartbeat = MagicMock()
        heartbeat.is_file.return_value = exists
        heartbeat.stat.return_value.st_mtime = mtime
        current = MagicMock()
        current.astimezone.return_value = _MOMENT

        with (
            patch(
                "app.services.gocryptfs_health.get_config",
                return_value=_config(),
            ),
            patch(
                "app.services.gocryptfs_health.is_cipherdir_created",
                new=AsyncMock(
                    return_value=flags["is_cipherdir_created"],
                ),
            ) as cipherdir,
            patch(
                "app.services.gocryptfs_health.ismount",
                new=AsyncMock(
                    return_value=flags["is_cipherdir_mounted"],
                ),
            ) as mounted,
            patch(
                "app.services.gocryptfs_health.is_versity_created",
                new=AsyncMock(return_value=flags["is_versity_created"]),
            ) as versity_created,
            patch(
                "app.services.gocryptfs_health.is_versity_running",
                new=AsyncMock(return_value=flags["is_versity_running"]),
            ) as versity_running,
            patch(
                "app.services.gocryptfs_health.Path",
                return_value=heartbeat,
            ) as path,
            patch(
                "app.services.gocryptfs_health.time.time",
                return_value=1000.0,
            ),
            patch(
                "app.services.gocryptfs_health.datetime",
            ) as clock,
        ):
            clock.now.return_value = current
            result = await gocryptfs_health()

        path.assert_called_once_with(WATCHDOG_HEARTBEAT_PATH)
        cipherdir.assert_awaited_once_with("/cipher")
        mounted.assert_awaited_once_with("/mount")
        versity_created.assert_awaited_once_with(
            "/secrets/access",
            "/secrets/secret",
        )
        versity_running.assert_awaited_once_with()
        clock.now.assert_called_once_with()
        current.astimezone.assert_called_once_with()
        if exists:
            heartbeat.stat.assert_called_once_with()
        else:
            heartbeat.stat.assert_not_called()
        return result


class TestTimezoneName(unittest.TestCase):
    def test_uses_iana_name(self):
        moment = MagicMock()
        moment.tzinfo = _Zone()

        self.assertEqual(_timezone_name(moment), "Asia/Tbilisi")

    def test_uses_tzname_without_iana_key(self):
        moment = MagicMock()
        moment.tzinfo = object()
        moment.tzname.return_value = "GET"

        self.assertEqual(_timezone_name(moment), "GET")

    def test_uses_utc_without_timezone(self):
        moment = MagicMock()
        moment.tzinfo = None

        self.assertEqual(_timezone_name(moment), "UTC")

    def test_uses_local_when_name_is_empty(self):
        for label in ("", None):
            with self.subTest(label=label):
                moment = MagicMock()
                moment.tzinfo = object()
                moment.tzname.return_value = label

                self.assertEqual(_timezone_name(moment), "local")


class TestLocalAwareNow(unittest.TestCase):
    def test_returns_aware_local_time(self):
        current = MagicMock()
        current.astimezone.return_value = _MOMENT

        with patch("app.services.gocryptfs_health.datetime") as clock:
            clock.now.return_value = current
            result = _local_aware_now()

        self.assertIs(result, _MOMENT)
        clock.now.assert_called_once_with()
        current.astimezone.assert_called_once_with()
