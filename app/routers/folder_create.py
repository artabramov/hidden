# app/routers/folder_create.py
# SPDX-License-Identifier: GPL-3.0-only

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.auth import AccessLevel, require_access
from app.dependencies.session import get_session
from app.models.user import User
from app.schemas.folder_create import (
    FOLDER_CREATE_ERRORS,
    FolderCreateRequest,
    FolderCreateResponse,
)
from app.services.folder_create import create_folder

router = APIRouter(tags=["Folders"])


@router.post(
    "/folder",
    response_model=FolderCreateResponse,
    responses=FOLDER_CREATE_ERRORS,
    status_code=status.HTTP_201_CREATED,
    summary="Create folder",
)
async def folder_create_router(
    data: FolderCreateRequest,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_access(AccessLevel.WRITE)),
) -> FolderCreateResponse:
    """
    Creates a new folder in the root or under the specified parent
    folder. The parent folder must exist and must not be write-protected.

    **Hooks:**

    `FOLDER_CREATE_COMPLETED` — executed after the folder is
    successfully created.

    **Authentication:**

    - Requires a valid token with write access or higher.

    **Request body:**

    - `FolderCreateRequest` — parent folder ID, dirname, and optional
      summary.

    **Response:**

    `FolderCreateResponse` — created folder ID.

    **Response codes:**

    - `201` — Folder created successfully.
    - `401` — Invalid, expired, or missing token.
    - `403` — User inactive, blocked, or lacks writer access.
    - `404` — Parent folder was not found.
    - `409` — Folder dirname already exists in the target parent.
    - `422` — Input values failed validation.
    - `423` — Target parent folder is write-protected.
    - `503` — Service temporarily unavailable.
    """
    folder = await create_folder(
        session=session,
        user=current_user,
        data=data,
    )
    return FolderCreateResponse.model_validate(folder)
