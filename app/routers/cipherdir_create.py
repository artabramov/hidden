# app/routers/cipherdir_create.py
# SPDX-License-Identifier: SSPL-1.0

from fastapi import APIRouter, Response, status

from app.schemas.cipherdir_create import (
    CIPHERDIR_CREATE_ERRORS,
    CipherdirCreateRequest,
)
from app.services.cipherdir_create import create_cipherdir

router = APIRouter(tags=["Initialization"])


@router.post(
    "/init/cipherdir",
    responses=CIPHERDIR_CREATE_ERRORS,
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Initialize gocryptfs cipherdir (on first boot)",
)
async def create_cipherdir_router(
    data: CipherdirCreateRequest,
) -> Response:
    """
    Initializes encrypted application storage. It generates a strong
    random gocryptfs passphrase, encrypts it with the provided master
    password, and initializes the cipherdir. It also creates internal
    application keys used for JWT signing and symmetric encryption.

    This endpoint is intended for one-time initialization immediately
    after installation.

    **Authentication:**

    - Authentication is not required.

    **Request body:**

    - `CipherdirCreateRequest` — master password used to encrypt the
    generated gocryptfs passphrase.

    **Response:**

    Empty response body.

    **Response codes:**

    - `204` — Cipherdir initialized successfully.
    - `409` — Cipherdir already initialized.
    - `422` — Input values failed validation.
    """
    await create_cipherdir(data.master_password)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
