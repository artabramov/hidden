# app/runtime/watchdog.py
# SPDX-License-Identifier: Apache-2.0

import asyncio
import logging
from pathlib import Path

from app.config import get_config
from app.constants import WATCHDOG_HEARTBEAT_PATH
from app.log import init_logging
from app.io import isdir, isfile, ismount
from app.runtime.cipherdir import cipherdir_unmount
from app.runtime.versity import versity_stop

log = logging.getLogger(__name__)


async def run_watchdog() -> None:
    """
    Run the watchdog to monitor the encrypted storage state. If the
    mountpoint is mounted, the watchdog triggers an emergency unmount
    when critical conditions are violated (missing secrets, missing
    passphrase, or application not running). If the mountpoint is not
    mounted, the watchdog ensures that VersityGW is stopped.
    """
    config = get_config()
    Path(WATCHDOG_HEARTBEAT_PATH).touch()

    if not await ismount(config.INSTALL_MOUNTPOINT):
        await versity_stop()
        return

    if not await isdir(config.INSTALL_SECRETS):
        log.warning("msg=watchdog_secrets_missing")
        await _emergency_unmount(config.INSTALL_MOUNTPOINT)
        return

    if not await isfile(config.GOCRYPTFS_PASSPHRASE_PATH):
        log.warning("msg=watchdog_passphrase_missing")
        await _emergency_unmount(config.INSTALL_MOUNTPOINT)
        return

    if not _is_application_running():
        log.warning("msg=watchdog_application_missing")
        await _emergency_unmount(config.INSTALL_MOUNTPOINT)
        return


def _is_application_running() -> bool:
    """
    Return whether the expected Uvicorn application process is running
    by scanning process command lines in /proc for both Uvicorn and
    app.main:app.
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


async def _emergency_unmount(mountpoint: str) -> None:
    """
    Stop VersityGW and unmount the encrypted filesystem. If VersityGW
    cannot be stopped, continue with the unmount to ensure that the
    decrypted filesystem is not left mounted.
    """
    try:
        await versity_stop()
    except Exception:
        pass

    await cipherdir_unmount(mountpoint)
    log.info("msg=watchdog_unmount_completed")


if __name__ == "__main__":
    init_logging()
    raise SystemExit(asyncio.run(run_watchdog()))
