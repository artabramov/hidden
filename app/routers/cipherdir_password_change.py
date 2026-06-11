# app/routers/cipherdir_password_change.py
# SPDX-License-Identifier: GPL-3.0-only

from fastapi import APIRouter, Response, status

from app.schemas.cipherdir_password_change import (
    CIPHERDIR_PASSWORD_CHANGE_ERRORS,
    CipherdirPasswordChangeRequest,
)
from app.services.cipherdir_password_change import change_cipherdir_password

router = APIRouter(tags=["Initialization"])


@router.patch(
    "/init/cipherdir/password",
    responses=CIPHERDIR_PASSWORD_CHANGE_ERRORS,
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Change master password for cipherdir",
)
async def change_cipherdir_password_router(
    data: CipherdirPasswordChangeRequest,
) -> Response:
    """
    Changes the master password that protects the stored gocryptfs
    passphrase. It decrypts the passphrase with the current password
    and encrypts it again with the new password.

    **Hooks:**

    `CIPHERDIR_PASSWORD_CHANGE_COMPLETED` — executed after password
    rotation completes.

    **Authentication:**

    - Does not require a user token. Requires a valid master password.

    **Request body:**

    - `CipherdirPasswordChangeRequest` — current and new master
    passwords.

    **Response codes:**

    - `204` — Master password changed successfully.
    - `404` — Cipherdir not initialized.
    - `422` — Input values failed validation.
    - `429` — Master password attempts throttled.
    """
    await change_cipherdir_password(
        current_master_password=data.current_master_password,
        changed_master_password=data.changed_master_password,
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)
