# app/routers/gocryptfs_unmount.py
# SPDX-License-Identifier: Apache-2.0

from fastapi import APIRouter, Depends, Response, status

from app.dependencies.require_gocryptfs import require_gocryptfs
from app.schemas.gocryptfs_auth import GocryptfsAuthRequest
from app.services.gocryptfs_unmount import gocryptfs_unmount

router = APIRouter(tags=["gocryptfs"])


@router.post(
    "/gocryptfs/unmount",
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
                "is not initialized, not mounted, or the required "
                "passphrase is missing."
            ),
        },
    },
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_gocryptfs())],
    summary="Unmount gocryptfs cipherdir.",
)
async def gocryptfs_unmount_router(
    data: GocryptfsAuthRequest,
) -> Response:
    """
    Unmounts encrypted application storage. It verifies the master
    password by decrypting the stored gocryptfs passphrase, then
    unmounts the cipherdir.
    """
    await gocryptfs_unmount(master_password=data.master_password)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
