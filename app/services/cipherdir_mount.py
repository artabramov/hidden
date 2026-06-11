# app/services/cipherdir_mount.py
# SPDX-License-Identifier: GPL-3.0-only

import logging

from app.config import get_config
from app.constants import (
    GOCRYPTFS_CIPHERDIR_LOCK_PATH,
    OBSCURED_VALUE,
)
from app.db.migrations import check_db_integrity, upgrade_db
from app.errors import (
    ResourceConflictError,
    ResourceNotFoundError,
    TooManyRequestsError,
    ValueInvalidError,
)
from app.events import Events as E
from app.hooks import hooks
from app.locks import LockType, locks
from app.repositories.file import isdir, isfile, ismount, mkdir, read
from app.runtime.gocryptfs import (
    is_gocryptfs_initialized,
    mount_gocryptfs,
    unmount_gocryptfs,
)
from app.security.cipherdir import is_master_password_attempt_throttled
from app.security.encryption import decrypt_passphrase

log = logging.getLogger(__name__)


# TODO: Add garbage cleaning (removal of possible file system artifacts)
# when cipherdir mounting.

async def mount_cipherdir(
    master_password: str,
) -> None:
    """
    Mount the encrypted storage by decrypting the stored passphrase
    with the master password, mounting the gocryptfs filesystem,
    ensuring the SQLite directory exists, and initializing the
    database. If a post-mount step fails, the mount is rolled back.
    """
    if await is_master_password_attempt_throttled():
        raise TooManyRequestsError

    log.info("event=%s", E.CIPHERDIR_MOUNT_STARTED)
    config = get_config()

    async with locks.lock_file(
        GOCRYPTFS_CIPHERDIR_LOCK_PATH,
        LockType.WRITE,
    ):
        if not await is_gocryptfs_initialized(config.GOCRYPTFS_CIPHERDIR):
            log.warning("event=%s", E.CIPHERDIR_MOUNT_CIPHERDIR_NOT_CREATED)
            raise ResourceNotFoundError

        if not await isfile(config.GOCRYPTFS_PASSPHRASE_ENCRYPTED_PATH):
            log.warning("event=%s", E.CIPHERDIR_MOUNT_PASSPHRASE_MISSING)
            raise ResourceNotFoundError

        if await ismount(config.GOCRYPTFS_MOUNTPOINT):
            log.warning("event=%s", E.CIPHERDIR_MOUNT_ALREADY_MOUNTED)
            raise ResourceConflictError

        passphrase_encrypted = await read(
            config.GOCRYPTFS_PASSPHRASE_ENCRYPTED_PATH,
        )

        try:
            passphrase_bytes = decrypt_passphrase(
                passphrase_encrypted,
                master_password.encode("utf-8"),
            )
        except ValueError:
            log.warning("event=%s", E.CIPHERDIR_MOUNT_PASSPHRASE_INVALID)
            raise ValueInvalidError(
                field="master_password",
                input_value=OBSCURED_VALUE,
            )

        if not await isdir(config.GOCRYPTFS_MOUNTPOINT):
            await mkdir(config.GOCRYPTFS_MOUNTPOINT)

        await mount_gocryptfs(
            passphrase=passphrase_bytes.decode("utf-8"),
            cipherdir=config.GOCRYPTFS_CIPHERDIR,
            mountpoint=config.GOCRYPTFS_MOUNTPOINT,
        )

        try:
            if not await isdir(config.SQLITE_DIR):
                await mkdir(config.SQLITE_DIR)

            if not await isdir(config.FILES_DIR):
                await mkdir(config.FILES_DIR)

            if not await isdir(config.FILES_REVISIONS_DIR):
                await mkdir(config.FILES_REVISIONS_DIR)

            if not await isdir(config.FILES_THUMBNAILS_DIR):
                await mkdir(config.FILES_THUMBNAILS_DIR)

            if not await isdir(config.FILES_TMP_DIR):
                await mkdir(config.FILES_TMP_DIR)

            await upgrade_db()
            await check_db_integrity(config.SQLITE_PATH)

        except Exception:
            log.exception("event=%s", E.CIPHERDIR_MOUNT_FAILED)
            try:
                await unmount_gocryptfs(config.GOCRYPTFS_MOUNTPOINT)
                log.warning("event=%s", E.CIPHERDIR_MOUNT_ROLLBACK_COMPLETED)
            except Exception:
                log.exception("event=%s", E.CIPHERDIR_MOUNT_ROLLBACK_FAILED)
            raise

        log.info("event=%s", E.CIPHERDIR_MOUNT_COMPLETED)
        await hooks.emit(E.CIPHERDIR_MOUNT_COMPLETED)
