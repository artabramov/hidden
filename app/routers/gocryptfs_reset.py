# app/routers/gocryptfs_reset.py
# SPDX-License-Identifier: Apache-2.0

from fastapi import APIRouter, Depends, Response, status

from app.dependencies.require_gocryptfs import require_gocryptfs
from app.schemas.gocryptfs_auth import GocryptfsAuthRequest
from app.services.gocryptfs_reset import gocryptfs_reset

router = APIRouter(tags=["gocryptfs"])


@router.post(
    "/gocryptfs/reset",
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
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_gocryptfs(
        require_mountpoint=None,
    ))],
    summary="Reset encrypted storage.",
)
async def gocryptfs_reset_router(
    data: GocryptfsAuthRequest,
) -> Response:
    """
    Permanently remove all encrypted storage data and secrets after
    verifying the master password, returning Hidden to its
    uninitialized state.
    """
    await gocryptfs_reset(master_password=data.master_password)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
