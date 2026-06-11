# app/routers/cipherdir_unmount.py
# SPDX-License-Identifier: GPL-3.0-only

from fastapi import APIRouter, Response, status

from app.schemas.cipherdir_unmount import (
    CIPHERDIR_UNMOUNT_ERRORS,
    CipherdirUnmountRequest,
)
from app.services.cipherdir_unmount import unmount_cipherdir

router = APIRouter(tags=["Initialization"])


@router.post(
    "/init/cipherdir/unmount",
    responses=CIPHERDIR_UNMOUNT_ERRORS,
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Unmount gocryptfs cipherdir",
)
async def unmount_cipherdir_router(
    data: CipherdirUnmountRequest,
) -> Response:
    """
    Unmounts encrypted application storage. It decrypts the stored
    gocryptfs passphrase with the provided master password and uses
    it to unmount the cipherdir.

    **Hooks:**

    `CIPHERDIR_UNMOUNT_COMPLETED` — executed after storage is unmounted
    successfully.

    **Authentication:**

    - Does not require a user token. Requires a valid master password.

    **Request body:**

    - `CipherdirUnmountRequest` — master password to verify before
    unmount.

    **Response codes:**

    - `204` — Cipherdir unmounted successfully.
    - `404` — Cipherdir not initialized.
    - `409` — Cipherdir not mounted.
    - `422` — Input values failed validation.
    - `429` — Master password attempts throttled.
    """
    await unmount_cipherdir(
        master_password=data.master_password,
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)
