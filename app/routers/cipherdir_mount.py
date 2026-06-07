# app/routers/cipherdir_mount.py
# SPDX-License-Identifier: SSPL-1.0

from fastapi import APIRouter, Response, status

from app.schemas.cipherdir_mount import (
    CIPHERDIR_MOUNT_ERRORS,
    CipherdirMountRequest,
)
from app.services.cipherdir_mount import mount_cipherdir

router = APIRouter(tags=["Initialization"])


@router.post(
    "/init/cipherdir/mount",
    responses=CIPHERDIR_MOUNT_ERRORS,
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Mount gocryptfs cipherdir",
)
async def mount_cipherdir_router(
    data: CipherdirMountRequest,
) -> Response:
    """
    Mounts encrypted application storage. It decrypts the stored
    gocryptfs passphrase with the provided master password and uses
    it to mount the cipherdir.

    **Hooks:**

    `CIPHERDIR_MOUNT_COMPLETED` — executed after storage is mounted
    successfully.

    **Authentication:**

    - Does not require a user token. Requires a valid master password.

    **Request body:**

    - `CipherdirMountRequest` — master password to decrypt the stored
    passphrase and mount.

    **Response codes:**

    - `204` — Cipherdir mounted successfully.
    - `404` — Cipherdir not initialized.
    - `409` — Cipherdir already mounted.
    - `422` — Input values failed validation.
    - `429` — Master password attempts throttled.
    """
    await mount_cipherdir(
        master_password=data.master_password,
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)
