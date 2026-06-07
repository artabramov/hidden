# app/routers/file_starred_change.py
# SPDX-License-Identifier: SSPL-1.0

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.auth import AccessLevel, require_access
from app.dependencies.session import get_session
from app.models.user import User
from app.schemas.file_starred_change import (
    FILE_STARRED_ERRORS,
    FileStarredChangeRequest,
    FileStarredChangeResponse,
)
from app.services.file_starred_change import change_file_starred

router = APIRouter(tags=["Files"])


@router.patch(
    "/file/{file_id}/starred",
    response_model=FileStarredChangeResponse,
    responses=FILE_STARRED_ERRORS,
    status_code=status.HTTP_200_OK,
    summary="Change file starred flag",
)
async def file_starred_change_router(
    file_id: int,
    data: FileStarredChangeRequest,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_access(AccessLevel.EDIT)),
) -> FileStarredChangeResponse:
    """
    Updates the starred flag for a file.

    **Hooks:**

    `FILE_STARRED_CHANGE_COMPLETED` — executed after the flag is updated.

    **Authentication:**

    - Requires edit access or higher.

    **Request path:**

    - `file_id` — ID of the target file.

    **Request body:**

    - `FileStarredChangeRequest` — new starred value.

    **Response:**

    `FileStarredChangeResponse` — identifier of the updated file.

    **Response codes:**

    - `200` — Updated successfully.
    - `401` — Invalid, expired, or missing token.
    - `403` — User inactive, blocked, or lacks access.
    - `404` — File not found.
    - `422` — Validation error.
    - `503` — Service unavailable.
    """
    updated = await change_file_starred(
        session=session,
        user=current_user,
        file_id=file_id,
        data=data,
    )

    return FileStarredChangeResponse.model_validate(updated)
