# app/routers/folder_select.py
# SPDX-License-Identifier: SSPL-1.0

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.auth import AccessLevel, require_access
from app.dependencies.session import get_session
from app.models.user import User
from app.schemas.folder_select import (
    FOLDER_SELECT_ERRORS,
    FolderSelectResponse,
    build_folder_response,
)
from app.services.folder_select import select_folder

router = APIRouter(tags=["Folders"])


@router.get(
    "/folder/{folder_id}",
    response_model=FolderSelectResponse,
    responses=FOLDER_SELECT_ERRORS,
    status_code=status.HTTP_200_OK,
    summary="Select folder by ID",
)
async def folder_select_router(
    folder_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_access(AccessLevel.READ)),
) -> FolderSelectResponse:
    """
    Returns folder metadata for the specified folder identifier.

    **Hooks:**

    `FOLDER_SELECT_COMPLETED` — executed after folder data is retrieved.

    **Authentication:**

    - Requires a valid token with read access or higher.

    **Request path:**

    - `folder_id` — ID of the folder to retrieve.

    **Response:**

    `FolderSelectResponse` — identifier, parent folder ID, dirname,
    summary, write-protection flag, and creation / update timestamps.

    **Response codes:**

    - `200` — Folder data returned successfully.
    - `401` — Invalid, expired, or missing token.
    - `403` — User inactive, blocked, or lacks read access.
    - `404` — Folder not found.
    - `422` — Input values failed validation.
    - `503` — Service temporarily unavailable.
    """
    folder, is_write_protected_recursive = await select_folder(
        session=session,
        folder_id=folder_id,
    )

    return build_folder_response(
        folder,
        is_write_protected_recursive,
    )
