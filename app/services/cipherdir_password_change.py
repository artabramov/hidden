# app/services/cipherdir_password_change.py
# SPDX-License-Identifier: SSPL-1.0

import logging

from app.config import get_config
from app.constants import GOCRYPTFS_CIPHERDIR_LOCK_PATH, OBSCURED_VALUE
from app.errors import (
    ResourceNotFoundError,
    TooManyRequestsError,
    ValueInvalidError,
)
from app.events import Events as E
from app.hooks import hooks
from app.locks import LockType, locks
from app.repositories.file import isfile, read, write
from app.runtime.gocryptfs import is_gocryptfs_initialized
from app.security.cipherdir import is_master_password_attempt_throttled
from app.security.encryption import decrypt_passphrase, encrypt_passphrase

log = logging.getLogger(__name__)


async def change_cipherdir_password(
    current_master_password: str,
    changed_master_password: str,
) -> None:
    """
    Change the master password protecting the stored gocryptfs
    passphrase by decrypting it with the current password,
    re-encrypting it with the new password, and persisting it.
    """
    if await is_master_password_attempt_throttled():
        raise TooManyRequestsError

    log.info("event=%s", E.CIPHERDIR_PASSWORD_CHANGE_STARTED)
    config = get_config()

    async with locks.lock_file(
        GOCRYPTFS_CIPHERDIR_LOCK_PATH,
        LockType.WRITE,
    ):
        if not await is_gocryptfs_initialized(config.GOCRYPTFS_CIPHERDIR):
            log.warning("event=%s", E.CIPHERDIR_PASSWORD_CHANGE_CIPHERDIR_NOT_CREATED)  # noqa: E501
            raise ResourceNotFoundError

        if not await isfile(config.GOCRYPTFS_PASSPHRASE_ENCRYPTED_PATH):
            log.warning("event=%s", E.CIPHERDIR_PASSWORD_CHANGE_PASSPHRASE_MISSING)  # noqa: E501
            raise ResourceNotFoundError

        passphrase_encrypted = await read(
            config.GOCRYPTFS_PASSPHRASE_ENCRYPTED_PATH,
        )

        try:
            passphrase = decrypt_passphrase(
                passphrase_encrypted,
                current_master_password.encode("utf-8"),
            )
        except ValueError:
            log.warning("event=%s", E.CIPHERDIR_PASSWORD_CHANGE_PASSPHRASE_INVALID)  # noqa: E501
            raise ValueInvalidError(
                field="current_master_password",
                input_value=OBSCURED_VALUE,
            )

        passphrase_encrypted_changed = encrypt_passphrase(
            passphrase,
            changed_master_password.encode("utf-8"),
        )

        await write(
            config.GOCRYPTFS_PASSPHRASE_ENCRYPTED_PATH,
            passphrase_encrypted_changed,
        )

        log.info("event=%s", E.CIPHERDIR_PASSWORD_CHANGE_COMPLETED)
        await hooks.emit(E.CIPHERDIR_PASSWORD_CHANGE_COMPLETED)
