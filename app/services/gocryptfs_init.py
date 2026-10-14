# app/services/gocryptfs_init.py
# SPDX-License-Identifier: Apache-2.0

import logging
import os

from app.config import get_config
from app.constants import GOCRYPTFS_PASSPHRASE_LENGTH
from app.errors import BadGatewayError
from app.locks import lock_manager
from app.io import delete, isfile, write
from app.security.encryption import encrypt_passphrase
from app.security.randoms import generate_random_string
from app.runtime.cipherdir import cipherdir_create, is_cipherdir_created
from app.runtime.versity import versity_create, is_versity_created

log = logging.getLogger(__name__)

# NOTE (ADR-04): gocryptfs passphrase is protected by master password.
# It is encrypted with a master password and is never persisted in
# plaintext on disk. The passphrase exists in plaintext only in memory
# during mount and is discarded immediately afterwards. Access to the
# encrypted data therefore requires both the passphrase and the master
# password.

# NOTE (ADR-05): gocryptfs passphrase is provided through tmpfs.
# Command-line arguments and stdin are avoided to prevent exposure
# in process listings (argv) and to bypass TTY-based input behavior.
# The passphrase is written to a temporary file in tmpfs (/dev/shm)
# and passed using -passfile. The file exists only for the duration
# of the mount operation and is removed immediately after use.

# NOTE (ADR-06): Cipherdir initialization is a one-time operation.
# The service creates the gocryptfs filesystem and all related secrets
# together. This operation is not transactional, so on failure the
# service performs best-effort cleanup of artifacts created during
# the current attempt.


async def gocryptfs_init(master_password: str) -> tuple[str, str]:
    """
    Initialize encrypted storage by generating and encrypting a random
    gocryptfs passphrase, initializing the cipherdir, creating the
    VersityGW root credentials, and persisting all created secrets.

    Initialization is not transactional. If any step fails, the
    function performs best-effort cleanup of artifacts created during
    the current attempt.
    """
    config = get_config()

    async with lock_manager.lock():
        if await isfile(config.GOCRYPTFS_PASSPHRASE_PATH):
            log.warning("msg=gocryptfs_passphrase_already_exists")
            raise BadGatewayError

        if await is_cipherdir_created(config.INSTALL_CIPHERDIR):
            log.warning("msg=cipherdir_already_exists")
            raise BadGatewayError

        if await is_versity_created(
            config.VERSITY_ACCESS_KEY_PATH,
            config.VERSITY_SECRET_KEY_PATH,
        ):
            log.warning("msg=versity_already_exists")
            raise BadGatewayError

        passphrase = generate_random_string(GOCRYPTFS_PASSPHRASE_LENGTH)
        passphrase_encrypted = encrypt_passphrase(
            passphrase.encode("utf-8"),
            master_password.encode("utf-8"),
        )

        try:
            await write(
                config.GOCRYPTFS_PASSPHRASE_PATH,
                passphrase_encrypted,
            )

            await cipherdir_create(
                passphrase,
                config.INSTALL_CIPHERDIR
            )

            access_key, secret_key = await versity_create(
                config.VERSITY_ACCESS_KEY_PATH,
                config.VERSITY_SECRET_KEY_PATH,
            )

        except Exception:
            log.exception("msg=gocryptfs_initialization_failed")

            await delete(config.GOCRYPTFS_PASSPHRASE_PATH)

            await delete(os.path.join(
                config.INSTALL_CIPHERDIR,
                "gocryptfs.conf"
            ))

            await delete(os.path.join(
                config.INSTALL_CIPHERDIR,
                "gocryptfs.diriv"
            ))

            await delete(config.VERSITY_ACCESS_KEY_PATH)
            await delete(config.VERSITY_SECRET_KEY_PATH)

            raise

    return access_key, secret_key
