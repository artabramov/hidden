# app/routers/file_rotate.py
# SPDX-License-Identifier: SSPL-1.0

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.auth import AccessLevel, require_access
from app.dependencies.session import get_session
from app.models.user import User
from app.schemas.file_rotate import (
    FILE_ROTATE_ERRORS,
    FileRotateRequest,
    FileRotateResponse,
)
from app.services.file_rotate import rotate_file

router = APIRouter(tags=["Files"])


@router.post(
    "/file/{file_id}/rotate",
    response_model=FileRotateResponse,
    responses=FILE_ROTATE_ERRORS,
    status_code=status.HTTP_200_OK,
    summary="Rotate image file",
)
async def file_rotate_router(
    file_id: int,
    data: FileRotateRequest,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_access(AccessLevel.EDIT)),
) -> FileRotateResponse:
    """
    Rotates an image file clockwise by the specified angle. A new file
    revision is created for every successful rotation.

    **Hooks:**

    `FILE_ROTATE_COMPLETED` — executed after the file is successfully
    rotated.

    **Authentication:**

    - Requires a valid token with edit access or higher.

    **Request path:**

    - `file_id` — ID of the target file.

    **Request body:**

    - `FileRotateRequest` — rotation angle (90, 180, 270).

    **Response:**

    `FileRotateResponse` — identifier of the rotated file.

    **Response codes:**

    - `200` — File rotated successfully.
    - `401` — Invalid, expired, or missing token.
    - `403` — User inactive, blocked, or lacks edit access.
    - `404` — Target file not found.
    - `409` — File is not an image or unsupported format.
    - `422` — Input validation error.
    - `423` — Parent folder is write-protected.
    - `503` — Service temporarily unavailable.
    """
    rotated = await rotate_file(
        session=session,
        user=current_user,
        file_id=file_id,
        data=data,
    )

    return FileRotateResponse.model_validate(rotated)
