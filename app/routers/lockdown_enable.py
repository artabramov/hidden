# app/routers/lockdown_enable.py
# SPDX-License-Identifier: SSPL-1.0

from fastapi import APIRouter, Response, status

from app.schemas.lockdown_enable import (
    LOCKDOWN_ENABLE_ERRORS,
    LockdownEnableRequest,
)
from app.services.lockdown_enable import enable_lockdown

router = APIRouter(tags=["Initialization"])


@router.post(
    "/init/lockdown/enable",
    responses=LOCKDOWN_ENABLE_ERRORS,
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Enable lockdown mode",
)
async def enable_lockdown_router(
    data: LockdownEnableRequest,
) -> Response:
    """
    Enables lockdown mode for the application. It decrypts the stored
    gocryptfs passphrase using the provided master password and sets
    the lockdown state.

    **Hooks:**

    `LOCKDOWN_ENABLE_COMPLETED` — executed after lockdown mode is
    enabled.

    **Authentication:**

    - Does not require a user token. Requires a valid master password.

    **Request body:**

    - `LockdownEnableRequest` — master password for verification.

    **Response codes:**

    - `204` — Lockdown mode enabled successfully.
    - `404` — gocryptfs passphrase not found.
    - `409` — Lockdown mode already enabled.
    - `422` — Input values failed validation.
    - `429` — Master password attempts throttled.
    """
    await enable_lockdown(
        master_password=data.master_password,
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)
