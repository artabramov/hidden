# app/services/gocryptfs_reveal.py
# SPDX-License-Identifier: Apache-2.0

import logging

from app.config import get_config
from app.errors import UnauthorizedError
from app.locks import lock_manager
from app.io import read
from app.security.encryption import decrypt_passphrase

log = logging.getLogger(__name__)


async def gocryptfs_reveal(master_password: str) -> tuple[str, str, str]:
    """
    Decrypt and return the stored gocryptfs passphrase using the
    provided master password.
    """
    config = get_config()

    async with lock_manager.lock():
        passphrase_encrypted = await read(config.GOCRYPTFS_PASSPHRASE_PATH)

        try:
            passphrase = decrypt_passphrase(
                passphrase_encrypted,
                master_password.encode("utf-8"),
            )

        except ValueError:
            log.warning("msg=passphrase_invalid")
            raise UnauthorizedError

        versity_access_key = (
            await read(config.VERSITY_ACCESS_KEY_PATH)
        ).decode("utf-8")

        versity_secret_key = (
            await read(config.VERSITY_SECRET_KEY_PATH)
        ).decode("utf-8")

        return (
            passphrase.decode("utf-8"),
            versity_access_key,
            versity_secret_key,
        )
