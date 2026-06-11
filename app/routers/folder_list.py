# app/routers/folder_list.py
# SPDX-License-Identifier: GPL-3.0-only

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.auth import AccessLevel, require_access
from app.dependencies.session import get_session
from app.models.user import User
from app.schemas.folder_list import (
    FOLDER_LIST_ERRORS,
    FolderListRequest,
    FolderListResponse,
)
from app.schemas.folder_select import build_folder_response
from app.services.folder_list import list_folders

router = APIRouter(tags=["Folders"])


@router.get(
    "/folders",
    response_model=FolderListResponse,
    responses=FOLDER_LIST_ERRORS,
    status_code=status.HTTP_200_OK,
    summary="List folders",
)
async def folder_root_list_router(
    session: AsyncSession = Depends(get_session),
    params: FolderListRequest = Depends(),
    current_user: User = Depends(require_access(AccessLevel.READ)),
) -> FolderListResponse:
    """
    Returns folders of the root or of the given parent folder.

    **Hooks:**

    `FOLDER_LIST_COMPLETED` — executed after folder list is retrieved.

    **Authentication:**

    - Requires a valid token with read access or higher.

    **Response:**

    `FolderListResponse` — list of folders with metadata and total count.

    **Response codes:**

    - `200` — Folder list returned successfully.
    - `401` — Invalid, expired, or missing token.
    - `403` — User inactive, blocked, or lacks read access.
    - `404` — Parent folder not found (when set).
    - `422` — Input values failed validation.
    - `503` — Service temporarily unavailable.
    """
    folders, folders_count, is_write_protected_recursive = await list_folders(
        session=session,
        params=params,
    )

    return FolderListResponse(
        folders=[
            build_folder_response(folder, is_write_protected_recursive)
            for folder in folders
        ],
        folders_count=folders_count,
    )
