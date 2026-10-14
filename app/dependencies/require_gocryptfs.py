# app/dependencies/require_gocryptfs.py
# SPDX-License-Identifier: Apache-2.0

import logging

from app.config import get_config
from app.errors import ServiceUnavailableError, BadGatewayError
from app.runtime.cipherdir import is_cipherdir_created
from app.io import isfile, ismount

log = logging.getLogger(__name__)


def require_gocryptfs(
    require_cipherdir: bool | None = True,
    require_mountpoint: bool | None = True,
    require_passphrase: bool | None = True,
):
    """
    Create a FastAPI dependency that validates the required, forbidden,
    or ignored state of the gocryptfs cipherdir, mountpoint, and
    passphrase.
    """

    async def check_gocryptfs() -> None:
        """
        Validate the configured gocryptfs cipherdir, mountpoint, and
        passphrase states and reject the request if any required or
        forbidden condition is not satisfied.
        """
        config = get_config()

        # Scenario 1: validate cipherdir existence or absence

        if require_cipherdir is True:
            if not await is_cipherdir_created(config.INSTALL_CIPHERDIR):
                log.warning("msg=cipherdir_not_found")
                raise ServiceUnavailableError

        elif require_cipherdir is False:
            if await is_cipherdir_created(config.INSTALL_CIPHERDIR):
                log.warning("msg=cipherdir_exists")
                raise BadGatewayError

        # Scenario 2: validate mountpoint existence or absence

        if require_mountpoint is True:
            if not await ismount(config.INSTALL_MOUNTPOINT):
                log.warning("msg=mountpoint_not_found")
                raise ServiceUnavailableError

        elif require_mountpoint is False:
            if await ismount(config.INSTALL_MOUNTPOINT):
                log.warning("msg=mountpoint_exists")
                raise BadGatewayError

        # Scenario 3: validate passphrase existence or absence

        if require_passphrase is True:
            if not await isfile(config.GOCRYPTFS_PASSPHRASE_PATH):
                log.warning("msg=passphrase_not_found")
                raise ServiceUnavailableError

        elif require_passphrase is False:
            if await isfile(config.GOCRYPTFS_PASSPHRASE_PATH):
                log.warning("msg=passphrase_exists")
                raise BadGatewayError

    return check_gocryptfs
