# app/services/health_check.py
# SPDX-License-Identifier: SSPL-1.0

import time
from datetime import datetime
from pathlib import Path

from app.config import get_config
from app.constants import (
    LOCKDOWN_MODE_ENABLED_FLAG_PATH,
    WATCHDOG_HEARTBEAT_PATH,
)
from app.repositories.file import isfile, ismount
from app.runtime.gocryptfs import is_gocryptfs_initialized


async def health_check() -> dict:
    """
    Return current health snapshot of the system.

    Checks runtime state: lockdown flag, first-admin bootstrap marker
    on the secrets volume, gocryptfs initialization, mountpoint status,
    and watchdog liveness. Also returns current local time metadata.

    Watchdog is considered alive if the heartbeat file exists and its
    mtime is within GOCRYPTFS_WATCHDOG_LIVENESS_SECONDS.
    """
    config = get_config()

    is_lockdown_mode_enabled = await isfile(LOCKDOWN_MODE_ENABLED_FLAG_PATH)
    is_first_admin_created = await isfile(config.FIRST_ADMIN_CREATED_FLAG_PATH)
    is_cipherdir_created = await is_gocryptfs_initialized(config.GOCRYPTFS_CIPHERDIR)  # noqa: E501
    is_mountpoint_mounted = await ismount(config.GOCRYPTFS_MOUNTPOINT)

    watchdog_path = Path(WATCHDOG_HEARTBEAT_PATH)
    is_watchdog_alive = False
    if watchdog_path.is_file():
        watchdog_touch_time = watchdog_path.stat().st_mtime
        time_since_watchdog_touch = time.time() - watchdog_touch_time
        watchdog_threshold = config.GOCRYPTFS_WATCHDOG_LIVENESS_SECONDS
        is_watchdog_alive = time_since_watchdog_touch <= watchdog_threshold

    now_local = _local_aware_now()
    unix_timestamp = int(now_local.timestamp())
    timezone_name = _timezone_name(now_local)

    return {
        "is_lockdown_mode_enabled": is_lockdown_mode_enabled,
        "is_first_admin_created": is_first_admin_created,
        "is_cipherdir_created": is_cipherdir_created,
        "is_mountpoint_mounted": is_mountpoint_mounted,
        "is_watchdog_alive": is_watchdog_alive,
        "unix_timestamp": unix_timestamp,
        "timezone_name": timezone_name,
    }


def _local_aware_now() -> datetime:
    """Current instant as timezone-aware datetime in the host local zone."""
    return datetime.now().astimezone()


def _timezone_name(now_local: datetime) -> str:
    """Return IANA timezone name, fallback to tzname, UTC, or local."""
    tz = now_local.tzinfo
    if tz is None:
        return "UTC"
    iana = getattr(tz, "key", None)
    if iana:
        return iana
    label = now_local.tzname()
    if label:
        return label
    return "local"
