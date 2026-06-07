# app/services/lockdown_enable.py
# SPDX-License-Identifier: SSPL-1.0

import logging

from app.config import get_config
from app.constants import LOCKDOWN_MODE_ENABLED_FLAG_PATH, OBSCURED_VALUE
from app.errors import (
    ResourceConflictError,
    ResourceNotFoundError,
    TooManyRequestsError,
    ValueInvalidError,
)
from app.events import Events as E
from app.hooks import hooks
from app.locks import LockType, locks
from app.repositories.file import isfile, read, touch
from app.security.cipherdir import is_master_password_attempt_throttled
from app.security.encryption import decrypt_passphrase

log = logging.getLogger(__name__)


async def enable_lockdown(
    master_password: str,
) -> None:
    """
    Enable lockdown mode by verifying the master password against the
    stored encrypted passphrase and creating the lockdown flag file.
    """
    if await is_master_password_attempt_throttled():
        raise TooManyRequestsError

    log.info("event=%s", E.LOCKDOWN_ENABLE_STARTED)
    config = get_config()

    async with locks.lock_file(
        LOCKDOWN_MODE_ENABLED_FLAG_PATH,
        LockType.WRITE,
    ):
        if await isfile(LOCKDOWN_MODE_ENABLED_FLAG_PATH):
            log.warning("event=%s", E.LOCKDOWN_ENABLE_ALREADY_ENABLED)
            raise ResourceConflictError

        if not await isfile(config.GOCRYPTFS_PASSPHRASE_ENCRYPTED_PATH):
            log.warning("event=%s", E.LOCKDOWN_ENABLE_PASSPHRASE_MISSING)
            raise ResourceNotFoundError

        passphrase_encrypted = await read(
            config.GOCRYPTFS_PASSPHRASE_ENCRYPTED_PATH,
        )

        try:
            decrypt_passphrase(
                passphrase_encrypted,
                master_password.encode("utf-8"),
            )
        except ValueError:
            log.warning("event=%s", E.LOCKDOWN_ENABLE_PASSPHRASE_INVALID)
            raise ValueInvalidError(
                field="master_password",
                input_value=OBSCURED_VALUE,
            )

        await touch(LOCKDOWN_MODE_ENABLED_FLAG_PATH)

        log.info("event=%s", E.LOCKDOWN_ENABLE_COMPLETED)
        await hooks.emit(E.LOCKDOWN_ENABLE_COMPLETED)
