# app/routers/file_update.py
# SPDX-License-Identifier: GPL-3.0-only

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.auth import AccessLevel, require_access
from app.dependencies.session import get_session
from app.models.user import User
from app.schemas.file_update import (
    FILE_UPDATE_ERRORS,
    FileUpdateRequest,
    FileUpdateResponse,
)
from app.services.file_update import update_file

router = APIRouter(tags=["Files"])


@router.patch(
    "/file/{file_id}",
    response_model=FileUpdateResponse,
    responses=FILE_UPDATE_ERRORS,
    status_code=status.HTTP_200_OK,
    summary="Update file metadata",
)
async def file_update_router(
    file_id: int,
    data: FileUpdateRequest,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_access(AccessLevel.EDIT)),
) -> FileUpdateResponse:
    """
    Updates file metadata. The filename and summary can be changed.

    **Hooks:**

    `FILE_UPDATE_COMPLETED` — executed after the file metadata is
    successfully updated.

    **Authentication:**

    - Requires a valid token with edit access or higher.

    **Request path:**

    - `file_id` — ID of the target file.

    **Request body:**

    - `FileUpdateRequest` — new filename and optional summary.

    **Response:**

    `FileUpdateResponse` — identifier of the updated file.

    **Response codes:**

    - `200` — File metadata updated successfully.
    - `401` — Invalid, expired, or missing token.
    - `403` — User inactive, blocked, or lacks edit access.
    - `404` — Target file not found.
    - `409` — File conflict.
    - `422` — Input validation error.
    - `423` — Parent folder is write-protected.
    - `503` — Service temporarily unavailable.
    """
    updated = await update_file(
        session=session,
        user=current_user,
        file_id=file_id,
        data=data,
    )

    return FileUpdateResponse.model_validate(updated)
