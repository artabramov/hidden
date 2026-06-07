# app/services/cipherdir_unmount.py
# SPDX-License-Identifier: SSPL-1.0

import logging

from app.cache.lru import get_thumbnail_cache
from app.config import get_config
from app.constants import GOCRYPTFS_CIPHERDIR_LOCK_PATH, OBSCURED_VALUE
from app.errors import (
    ResourceConflictError,
    ResourceNotFoundError,
    TooManyRequestsError,
    ValueInvalidError,
)
from app.events import Events as E
from app.hooks import hooks
from app.locks import LockType, locks
from app.repositories.file import isfile, ismount, read
from app.runtime.gocryptfs import is_gocryptfs_initialized, unmount_gocryptfs
from app.security.cipherdir import is_master_password_attempt_throttled
from app.security.encryption import decrypt_passphrase

log = logging.getLogger(__name__)


async def unmount_cipherdir(
    master_password: str,
) -> None:
    """
    Unmount the encrypted storage by verifying the master password
    against the stored passphrase and unmounting the gocryptfs
    filesystem.
    """
    if await is_master_password_attempt_throttled():
        raise TooManyRequestsError

    log.info("event=%s", E.CIPHERDIR_UNMOUNT_STARTED)
    config = get_config()

    async with locks.lock_file(
        GOCRYPTFS_CIPHERDIR_LOCK_PATH,
        LockType.WRITE,
    ):
        if not await is_gocryptfs_initialized(config.GOCRYPTFS_CIPHERDIR):
            log.warning("event=%s", E.CIPHERDIR_UNMOUNT_CIPHERDIR_NOT_CREATED)
            raise ResourceNotFoundError

        if not await isfile(config.GOCRYPTFS_PASSPHRASE_ENCRYPTED_PATH):
            log.warning("event=%s", E.CIPHERDIR_UNMOUNT_PASSPHRASE_MISSING)
            raise ResourceNotFoundError

        if not await ismount(config.GOCRYPTFS_MOUNTPOINT):
            log.warning("event=%s", E.CIPHERDIR_UNMOUNT_ALREADY_UNMOUNTED)
            raise ResourceConflictError

        passphrase_encrypted = await read(
            config.GOCRYPTFS_PASSPHRASE_ENCRYPTED_PATH,
        )

        try:
            decrypt_passphrase(
                passphrase_encrypted,
                master_password.encode("utf-8"),
            )
        except ValueError:
            log.warning("event=%s", E.CIPHERDIR_UNMOUNT_PASSPHRASE_INVALID)
            raise ValueInvalidError(
                field="master_password",
                input_value=OBSCURED_VALUE,
            )

        # NOTE (ADR-11): Dispose connections before gocryptfs unmount.
        # SQLite writes may still be buffered through the FUSE layer
        # even after transactions are committed. Unmounting with active
        # SQLAlchemy connections can leave partially flushed SQLite
        # pages and corrupt the database on the next mount. dispose()
        # prevents new writes from being issued through the old mount
        # before the encrypted filesystem is torn down.
        from app.db.engine import engine  # noqa: PLC0415
        engine.sync_engine.dispose()

        await unmount_gocryptfs(
            mountpoint=config.GOCRYPTFS_MOUNTPOINT,
        )

        get_thumbnail_cache().evict_all()

        log.info("event=%s", E.CIPHERDIR_UNMOUNT_COMPLETED)
        await hooks.emit(E.CIPHERDIR_UNMOUNT_COMPLETED)
