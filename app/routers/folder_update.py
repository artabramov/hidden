# app/routers/folder_update.py
# SPDX-License-Identifier: GPL-3.0-only

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.auth import AccessLevel, require_access
from app.dependencies.session import get_session
from app.models.user import User
from app.schemas.folder_update import (
    FOLDER_UPDATE_ERRORS,
    FolderUpdateRequest,
)
from app.services.folder_update import update_folder

router = APIRouter(tags=["Folders"])


@router.patch(
    "/folder/{folder_id}",
    responses=FOLDER_UPDATE_ERRORS,
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Update folder",
)
async def folder_update_router(
    folder_id: int,
    data: FolderUpdateRequest,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_access(AccessLevel.EDIT)),
) -> Response:
    """
    Updates folder metadata.

    **Hooks:**

    `FOLDER_UPDATE_COMPLETED` — executed after folder data is updated.

    **Authentication:**

    - Requires a valid token with edit access.

    **Request path:**

    - `folder_id` — ID of the folder to update.

    **Request body:**

    `FolderUpdateRequest` — dirname and optional summary.

    **Response:**

    Empty response body.

    **Response codes:**

    - `204` — Folder data updated successfully.
    - `401` — Invalid, expired, or missing token.
    - `403` — User inactive, blocked, or lacks edit access.
    - `404` — Folder not found.
    - `409` — Folder dirname already exists in the same parent folder.
    - `422` — Input values failed validation.
    - `423` — Target folder is write-protected.
    - `503` — Service temporarily unavailable.
    """
    await update_folder(
        session=session,
        user=current_user,
        folder_id=folder_id,
        data=data,
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)
