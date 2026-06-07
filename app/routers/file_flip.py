# app/routers/file_flip.py
# SPDX-License-Identifier: SSPL-1.0

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.auth import AccessLevel, require_access
from app.dependencies.session import get_session
from app.models.user import User
from app.schemas.file_flip import (
    FILE_FLIP_ERRORS,
    FileFlipRequest,
    FileFlipResponse,
)
from app.services.file_flip import flip_file

router = APIRouter(tags=["Files"])


@router.post(
    "/file/{file_id}/flip",
    response_model=FileFlipResponse,
    responses=FILE_FLIP_ERRORS,
    status_code=status.HTTP_200_OK,
    summary="Flip image file",
)
async def file_flip_router(
    file_id: int,
    data: FileFlipRequest,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_access(AccessLevel.EDIT)),
) -> FileFlipResponse:
    """
    Flips an image file by the specified axis. A new file revision is
    created for every successful flip.

    **Hooks:**

    `FILE_FLIP_COMPLETED` — executed after the file is successfully
    flipped.

    **Authentication:**

    - Requires a valid token with edit access or higher.

    **Request path:**

    - `file_id` — ID of the target file.

    **Request body:**

    - `FileFlipRequest` — flip axis (horizontal, vertical).

    **Response:**

    `FileFlipResponse` — identifier of the flipped file.

    **Response codes:**

    - `200` — File flipped successfully.
    - `401` — Invalid, expired, or missing token.
    - `403` — User inactive, blocked, or lacks edit access.
    - `404` — Target file not found.
    - `409` — File is not an image or unsupported format.
    - `422` — Input validation error.
    - `423` — Parent folder is write-protected.
    - `503` — Service temporarily unavailable.
    """
    flipped = await flip_file(
        session=session,
        user=current_user,
        file_id=file_id,
        data=data,
    )

    return FileFlipResponse.model_validate(flipped)
