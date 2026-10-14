# app/routers/gocryptfs_mount.py
# SPDX-License-Identifier: Apache-2.0

from fastapi import APIRouter, Depends, Response, status

from app.dependencies.require_gocryptfs import require_gocryptfs
from app.schemas.gocryptfs_auth import GocryptfsAuthRequest
from app.services.gocryptfs_mount import gocryptfs_mount

router = APIRouter(tags=["gocryptfs"])


@router.post(
    "/gocryptfs/mount",
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
        502: {
            "description": (
                "Gocryptfs infrastructure is in a conflicting state: "
                "the cipherdir is already mounted."
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
    dependencies=[Depends(require_gocryptfs(require_mountpoint=False))],
    summary="Mount gocryptfs cipherdir.",
)
async def gocryptfs_mount_router(
    data: GocryptfsAuthRequest,
) -> Response:
    """
    Mounts encrypted application storage. It decrypts the stored
    gocryptfs passphrase with the provided master password and uses
    that passphrase to mount the cipherdir.
    """
    await gocryptfs_mount(master_password=data.master_password)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
