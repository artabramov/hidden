# app/services/gocryptfs_reset.py
# SPDX-License-Identifier: Apache-2.0

import logging
import os

from app.config import get_config
from app.errors import UnauthorizedError
from app.io import delete, isdir, ismount, listdir, read, rmtree
from app.locks import lock_manager
from app.runtime.cipherdir import cipherdir_unmount
from app.runtime.versity import versity_stop
from app.security.encryption import decrypt_passphrase

log = logging.getLogger(__name__)


async def gocryptfs_reset(master_password: str) -> None:
    """
    Reset encrypted storage to its uninitialized state after verifying
    the master password. VersityGW is stopped, gocryptfs is unmounted,
    all encrypted data is removed, and stored secrets are deleted.
    """
    config = get_config()

    async with lock_manager.lock():
        passphrase_encrypted = await read(config.GOCRYPTFS_PASSPHRASE_PATH)

        try:
            decrypt_passphrase(
                passphrase_encrypted,
                master_password.encode("utf-8"),
            )

        except ValueError:
            log.warning("msg=passphrase_invalid")
            raise UnauthorizedError

        try:
            await versity_stop()
        except Exception:
            pass

        if await ismount(config.INSTALL_MOUNTPOINT):
            await cipherdir_unmount(
                mountpoint=config.INSTALL_MOUNTPOINT,
            )

        if await isdir(config.INSTALL_CIPHERDIR):
            for name in await listdir(config.INSTALL_CIPHERDIR):
                path = os.path.join(config.INSTALL_CIPHERDIR, name)

                if await isdir(path):
                    await rmtree(path)
                else:
                    await delete(path)

        await delete(config.GOCRYPTFS_PASSPHRASE_PATH)
        await delete(config.VERSITY_ACCESS_KEY_PATH)
        await delete(config.VERSITY_SECRET_KEY_PATH)
