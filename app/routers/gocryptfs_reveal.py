# app/routers/gocryptfs_reveal.py
# SPDX-License-Identifier: Apache-2.0

from fastapi import APIRouter, Depends, status

from app.dependencies.require_gocryptfs import require_gocryptfs
from app.schemas.gocryptfs_auth import GocryptfsAuthRequest
from app.schemas.gocryptfs_reveal import GocryptfsRevealResponse
from app.services.gocryptfs_reveal import gocryptfs_reveal

router = APIRouter(tags=["gocryptfs"])


@router.post(
    "/gocryptfs/reveal",
    responses={
        401: {
            "description": (
                "Master password is incorrect or the gocryptfs "
                "passphrase cannot be decrypted with it."
            ),
        },
        422: {
            "description": (
                "Request body failed basic Pydantic validation. "
                "This includes type validation, field constraints, "
                "and custom validators."
            ),
        },
        503: {
            "description": (
                "Gocryptfs infrastructure is not ready: cipherdir "
                "is not initialized or the required passphrase is "
                "missing."
            ),
        },
    },
    response_model=GocryptfsRevealResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_gocryptfs(require_mountpoint=None))],
    summary="Reveal storage secrets.",
)
async def gocryptfs_reveal_router(
    data: GocryptfsAuthRequest,
) -> GocryptfsRevealResponse:
    """
    Decrypts the stored gocryptfs passphrase with the provided master
    password and returns it together with the VersityGW root credentials.
    """
    passphrase, versity_access_key, versity_secret_key = (
        await gocryptfs_reveal(
            master_password=data.master_password,
        )
    )

    return GocryptfsRevealResponse(
        gocryptfs_passphrase=passphrase,
        versity_access_key=versity_access_key,
        versity_secret_key=versity_secret_key,
    )
