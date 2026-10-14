# app/services/gocryptfs_unmount.py
# SPDX-License-Identifier: Apache-2.0

import logging

from app.config import get_config
from app.errors import UnauthorizedError
from app.locks import lock_manager
from app.io import read
from app.runtime.cipherdir import cipherdir_unmount
from app.runtime.versity import versity_stop
from app.security.encryption import decrypt_passphrase

log = logging.getLogger(__name__)


async def gocryptfs_unmount(
    master_password: str,
) -> None:
    """
    Stop the VersityGW S3 server and unmount the encrypted storage
    after verifying the master password against the stored passphrase.
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

        await cipherdir_unmount(mountpoint=config.INSTALL_MOUNTPOINT)
