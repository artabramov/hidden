# app/routers/folder_delete.py
# SPDX-License-Identifier: SSPL-1.0

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.auth import AccessLevel, require_access
from app.dependencies.session import get_session
from app.models.user import User
from app.schemas.folder_delete import FOLDER_DELETE_ERRORS
from app.services.folder_delete import delete_folder

router = APIRouter(tags=["Folders"])


@router.delete(
    "/folder/{folder_id}",
    responses=FOLDER_DELETE_ERRORS,
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete folder",
)
async def folder_delete_router(
    folder_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_access(AccessLevel.ADMIN)),
) -> Response:
    """
    Deletes an existing folder and all direct files inside it.
    Folders containing subfolders cannot be deleted.

    **Hooks:**

    `FOLDER_DELETE_COMPLETED` — executed after the folder is
    successfully deleted.

    **Authentication:**

    - Requires a valid token with admin access.

    **Request path:**

    - `folder_id` — ID of the target folder.

    **Response:**

    Empty response body.

    **Response codes:**

    - `204` — Folder deleted successfully.
    - `401` — Invalid, expired, or missing token.
    - `403` — User inactive, blocked, or lacks admin access.
    - `404` — Target folder was not found.
    - `409` — Target folder contains subfolders and cannot be deleted.
    - `422` — Input values failed validation.
    - `423` — Target folder or parent folder is write-protected.
    - `503` — Service temporarily unavailable.
    """
    await delete_folder(
        session=session,
        folder_id=folder_id,
    )

    return Response(status_code=status.HTTP_204_NO_CONTENT)
