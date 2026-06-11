# app/routers/folder_write_protect.py
# SPDX-License-Identifier: GPL-3.0-only

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.auth import AccessLevel, require_access
from app.dependencies.session import get_session
from app.models.user import User
from app.schemas.folder_write_protect import (
    FOLDER_WRITE_PROTECT_ERRORS,
    FolderWriteProtectRequest,
)
from app.services.folder_write_protect import (
    change_folder_write_protect,
)

router = APIRouter(tags=["Folders"])


@router.patch(
    "/folder/{folder_id}/protected",
    responses=FOLDER_WRITE_PROTECT_ERRORS,
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Change folder write protection",
)
async def folder_write_protect_router(
    folder_id: int,
    data: FolderWriteProtectRequest,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_access(AccessLevel.ADMIN)),
) -> Response:
    """
    Changes folder write-protection flag.

    **Hooks:**

    `FOLDER_WRITE_PROTECT_COMPLETED` — executed after the flag is
    changed.

    **Authentication:**

    - Requires a valid token with admin access.

    **Request path:**

    - `folder_id` — ID of the folder.

    **Request body:**

    `FolderWriteProtectRequest` — boolean flag.

    **Response:**

    Empty response body.

    **Response codes:**

    - `204` — Write protection updated successfully.
    - `401` — Invalid, expired, or missing token.
    - `403` — User inactive, blocked, or lacks admin access.
    - `404` — Folder not found.
    - `422` — Input values failed validation.
    - `503` — Service temporarily unavailable.
    """
    await change_folder_write_protect(
        session=session,
        user=current_user,
        folder_id=folder_id,
        data=data,
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)
