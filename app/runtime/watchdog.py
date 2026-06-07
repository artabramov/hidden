# app/runtime/watchdog.py
# SPDX-License-Identifier: SSPL-1.0

import asyncio
import logging
from pathlib import Path

from app.config import get_config
from app.constants import (
    LOCKDOWN_MODE_ENABLED_FLAG_PATH,
    WATCHDOG_GRACEFUL_UNMOUNT_SECONDS,
    WATCHDOG_HEARTBEAT_PATH,
)
from app.log import init_logging
from app.repositories.file import isdir, isfile, ismount, touch
from app.runtime.gocryptfs import unmount_gocryptfs

logger = logging.getLogger(__name__)

# NOTE (ADR-08): Watchdog performs lazy unmount with a grace period.
# Before unmount, lockdown mode is enabled to block new requests and
# allow in-flight requests to complete within a short grace period.
# The mountpoint is detached using the -z flag, preventing new access
# while existing file descriptors may continue to operate. Requests
# exceeding the grace period may fail with HTTP 500. Full handling of
# storage failures within request execution is intentionally avoided
# to keep runtime logic simple and predictable.


async def run_watchdog() -> None:
    """
    If the mountpoint is mounted, the watchdog triggers an emergency
    unmount when critical conditions are violated (missing secrets,
    missing passphrase, or application not running). Before unmount,
    lockdown mode is enabled and a short grace period may be applied
    to allow in-flight requests to complete.
    """
    config = get_config()
    Path(WATCHDOG_HEARTBEAT_PATH).touch()

    if not await ismount(config.GOCRYPTFS_MOUNTPOINT):
        return

    if not await isdir(config.INSTALL_SECRETS_DIR):
        logger.warning("secrets not found, unmount started")
        await _lockdown_and_unmount(soft_drain=True)
        logger.info("secrets not found, mountpoint unmounted")
        return

    if not await isfile(config.GOCRYPTFS_PASSPHRASE_ENCRYPTED_PATH):
        logger.warning("passphrase not found, unmount started")
        await _lockdown_and_unmount(soft_drain=True)
        logger.info("passphrase not found, mountpoint unmounted")
        return

    if not _is_application_running():
        logger.warning("application not running, unmount started")
        await _lockdown_and_unmount(soft_drain=False)
        logger.info("application not running, mountpoint unmounted")


async def _lockdown_and_unmount(soft_drain: bool = True) -> None:
    """
    Enable lockdown mode and perform a lazy unmount of the mountpoint.
    Optionally waits for a short grace period to allow in-flight
    requests to complete before unmounting.
    """
    config = get_config()

    try:
        await touch(LOCKDOWN_MODE_ENABLED_FLAG_PATH)
    except OSError:
        logger.warning("failed to enable lockdown mode before unmount")

    if soft_drain:
        await asyncio.sleep(WATCHDOG_GRACEFUL_UNMOUNT_SECONDS)

    await unmount_gocryptfs(config.GOCRYPTFS_MOUNTPOINT)


def _is_application_running() -> bool:
    """
    Return whether a process matching the expected Uvicorn application
    command line is present in /proc.
    """
    proc_path = Path("/proc")

    try:
        entries = proc_path.iterdir()
    except OSError:
        return False

    for entry in entries:
        if not entry.name.isdigit():
            continue

        try:
            cmdline = (entry / "cmdline").read_bytes()
        except OSError:
            continue

        if not cmdline:
            continue

        if b"uvicorn" in cmdline and b"app.main:app" in cmdline:
            return True

    return False


if __name__ == "__main__":
    init_logging()
    raise SystemExit(asyncio.run(run_watchdog()))
