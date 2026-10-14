# app/services/gocryptfs_health.py
# SPDX-License-Identifier: Apache-2.0

import time
from datetime import datetime
from pathlib import Path

from app.config import get_config
from app.constants import WATCHDOG_HEARTBEAT_PATH
from app.io import ismount
from app.runtime.cipherdir import is_cipherdir_created
from app.runtime.versity import is_versity_created, is_versity_running


async def gocryptfs_health() -> dict:
    """
    Return the current gocryptfs runtime status.

    Suitable for client-side polling of cipherdir initialization,
    mount state, and watchdog liveness. The watchdog is considered
    alive if its heartbeat is recent.
    """
    config = get_config()

    cipherdir_created = await is_cipherdir_created(config.INSTALL_CIPHERDIR)
    cipherdir_mounted = await ismount(config.INSTALL_MOUNTPOINT)

    versity_created = await is_versity_created(
        config.VERSITY_ACCESS_KEY_PATH,
        config.VERSITY_SECRET_KEY_PATH,
    )
    versity_running = await is_versity_running()

    watchdog_path = Path(WATCHDOG_HEARTBEAT_PATH)
    watchdog_alive = False
    if watchdog_path.is_file():
        age = time.time() - watchdog_path.stat().st_mtime
        watchdog_alive = age <= config.WATCHDOG_LIVENESS_SECONDS

    now_local = _local_aware_now()

    return {
        "is_cipherdir_created": cipherdir_created,
        "is_cipherdir_mounted": cipherdir_mounted,
        "is_versity_created": versity_created,
        "is_versity_running": versity_running,
        "is_watchdog_alive": watchdog_alive,
        "unix_timestamp": int(now_local.timestamp()),
        "timezone_name": _timezone_name(now_local),
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
