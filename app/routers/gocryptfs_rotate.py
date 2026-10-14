# app/routers/gocryptfs_rotate.py
# SPDX-License-Identifier: Apache-2.0

from fastapi import APIRouter, Depends, Response, status

from app.dependencies.require_gocryptfs import require_gocryptfs
from app.schemas.gocryptfs_rotate import GocryptfsRotateRequest
from app.services.gocryptfs_rotate import gocryptfs_rotate

router = APIRouter(tags=["gocryptfs"])


@router.post(
    "/gocryptfs/rotate",
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
    dependencies=[Depends(require_gocryptfs(require_mountpoint=None))],
    summary="Rotate master password.",
)
async def gocryptfs_rotate_router(
    data: GocryptfsRotateRequest,
) -> Response:
    """
    Rotates the master password that protects the stored gocryptfs
    passphrase. It decrypts the passphrase with the current password
    and encrypts it again with the new password.
    """
    await gocryptfs_rotate(
        current_master_password=data.current_master_password,
        changed_master_password=data.changed_master_password,
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)
