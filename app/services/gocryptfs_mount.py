# app/services/gocryptfs_mount.py
# SPDX-License-Identifier: Apache-2.0

import logging

from app.config import get_config
from app.errors import UnauthorizedError
from app.locks import lock_manager
from app.io import isdir, mkdir, read
from app.runtime.cipherdir import cipherdir_mount, cipherdir_unmount
from app.runtime.versity import versity_start, versity_stop
from app.security.encryption import decrypt_passphrase

log = logging.getLogger(__name__)


# TODO: Add garbage cleaning (removal of possible file system artifacts)
# when cipherdir mounting.

async def gocryptfs_mount(master_password: str) -> None:
    """
    Mount the encrypted storage by decrypting the stored passphrase with
    the master password, mounting the gocryptfs filesystem, and starting
    the VersityGW S3 server.
    """
    config = get_config()

    async with lock_manager.lock():
        passphrase_encrypted = await read(config.GOCRYPTFS_PASSPHRASE_PATH)

        try:
            passphrase_bytes = decrypt_passphrase(
                passphrase_encrypted,
                master_password.encode("utf-8"),
            )

        except ValueError:
            log.warning("msg=passphrase_invalid")
            raise UnauthorizedError

        if not await isdir(config.INSTALL_MOUNTPOINT):
            await mkdir(config.INSTALL_MOUNTPOINT)

        await cipherdir_mount(
            passphrase=passphrase_bytes.decode("utf-8"),
            cipherdir=config.INSTALL_CIPHERDIR,
            mountpoint=config.INSTALL_MOUNTPOINT,
        )

        try:
            if not await isdir(config.VERSITY_DATA_PATH):
                await mkdir(config.VERSITY_DATA_PATH)

            if not await isdir(config.VERSITY_IAM_PATH):
                await mkdir(config.VERSITY_IAM_PATH)

            access_key = (
                await read(config.VERSITY_ACCESS_KEY_PATH)
            ).decode("utf-8")

            secret_key = (
                await read(config.VERSITY_SECRET_KEY_PATH)
            ).decode("utf-8")

            await versity_start(
                config.VERSITY_HOST,
                config.VERSITY_PORT,
                config.VERSITY_WEBGUI_HOST,
                config.VERSITY_WEBGUI_PORT,
                config.VERSITY_WEBGUI_GATEWAY,
                config.VERSITY_WEBGUI_CORS_ALLOW_ORIGIN,
                config.VERSITY_DATA_PATH,
                config.VERSITY_IAM_PATH,
                access_key,
                secret_key,
            )

        except Exception:
            log.exception("msg=gocryptfs_mount_failed")

            try:
                await versity_stop()
            except Exception:
                pass

            try:
                await cipherdir_unmount(config.INSTALL_MOUNTPOINT)
                log.warning("msg=gocryptfs_mount_rollback_completed")

            except Exception:
                log.exception("msg=gocryptfs_mount_rollback_failed")

            raise
