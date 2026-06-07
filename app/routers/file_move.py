# app/routers/file_move.py
# SPDX-License-Identifier: SSPL-1.0

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.auth import AccessLevel, require_access
from app.dependencies.session import get_session
from app.models.user import User
from app.schemas.file_move import (
    FILE_MOVE_ERRORS,
    FileMoveRequest,
    FileMoveResponse,
)
from app.services.file_move import move_file

router = APIRouter(tags=["Files"])


@router.post(
    "/file/{file_id}/move",
    response_model=FileMoveResponse,
    responses=FILE_MOVE_ERRORS,
    status_code=status.HTTP_200_OK,
    summary="Move file",
)
async def file_move_router(
    file_id: int,
    data: FileMoveRequest,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_access(AccessLevel.EDIT)),
) -> FileMoveResponse:
    """
    Moves an existing file to another folder. Source and destination
    folders must not be write-protected.

    **Hooks:**

    `FILE_MOVE_COMPLETED` — executed after the file is successfully
    moved.

    **Authentication:**

    - Requires a valid token with edit access or higher.

    **Request path:**

    - `file_id` — ID of the target file.

    **Request body:**

    - `FileMoveRequest` — destination folder ID.

    **Response:**

    `FileMoveResponse` — moved file ID and destination folder ID.

    **Response codes:**

    - `200` — File moved successfully.
    - `401` — Invalid, expired, or missing token.
    - `403` — User inactive, blocked, or lacks editor access.
    - `404` — Target file or destination folder was not found.
    - `409` — File conflict.
    - `422` — Input values failed validation.
    - `423` — Source or destination folder is write-protected.
    - `503` — Service temporarily unavailable.
    """
    moved = await move_file(
        session=session,
        user=current_user,
        file_id=file_id,
        data=data,
    )

    return FileMoveResponse.model_validate(moved)
