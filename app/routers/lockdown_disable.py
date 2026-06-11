# app/routers/lockdown_disable.py
# SPDX-License-Identifier: GPL-3.0-only

from fastapi import APIRouter, Response, status

from app.schemas.lockdown_disable import (
    LOCKDOWN_DISABLE_ERRORS,
    LockdownDisableRequest,
)
from app.services.lockdown_disable import disable_lockdown

router = APIRouter(tags=["Initialization"])


@router.post(
    "/init/lockdown/disable",
    responses=LOCKDOWN_DISABLE_ERRORS,
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Disable lockdown mode",
)
async def disable_lockdown_router(
    data: LockdownDisableRequest,
) -> Response:
    """
    Disables lockdown mode for the application. It decrypts the stored
    gocryptfs passphrase using the provided master password and clears
    the lockdown state.

    **Hooks:**

    `LOCKDOWN_DISABLE_COMPLETED` — executed after lockdown mode is
    disabled.

    **Authentication:**

    - Does not require a user token. Requires a valid master password.

    **Request body:**

    - `LockdownDisableRequest` — master password for verification.

    **Response codes:**

    - `204` — Lockdown mode disabled successfully.
    - `404` — gocryptfs passphrase not found.
    - `409` — Lockdown mode already disabled.
    - `422` — Input values failed validation.
    - `429` — Master password attempts throttled.
    """
    await disable_lockdown(
        master_password=data.master_password,
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)
