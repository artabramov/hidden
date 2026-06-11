# app/routers/file_edit.py
# SPDX-License-Identifier: GPL-3.0-only

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.auth import AccessLevel, require_access
from app.dependencies.session import get_session
from app.models.user import User
from app.schemas.file_edit import (
    FILE_EDIT_ERRORS,
    FileEditRequest,
    FileEditResponse,
)
from app.services.file_edit import edit_file

router = APIRouter(tags=["Files"])


@router.post(
    "/file/{file_id}/edit",
    response_model=FileEditResponse,
    responses=FILE_EDIT_ERRORS,
    status_code=status.HTTP_200_OK,
    summary="Edit text file",
)
async def file_edit_router(
    file_id: int,
    data: FileEditRequest,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_access(AccessLevel.EDIT)),
) -> FileEditResponse:
    """
    Edits a text file. A new file revision is created for every
    successful edit.

    **Hooks:**

    `FILE_EDIT_COMPLETED` — executed after the file is successfully
    edited.

    **Authentication:**

    - Requires a valid token with edit access or higher.

    **Request path:**

    - `file_id` — ID of the target file.

    **Request body:**

    - `FileEditRequest` — new file content.

    **Response:**

    `FileEditResponse` — identifier of the edited file.

    **Response codes:**

    - `200` — File edited successfully.
    - `401` — Invalid, expired, or missing token.
    - `403` — User inactive, blocked, or lacks edit access.
    - `404` — Target file not found.
    - `409` — File is not a text file or inconsistent state.
    - `422` — Input validation error.
    - `423` — Parent folder is write-protected.
    - `503` — Service temporarily unavailable.
    """
    edited = await edit_file(
        session=session,
        user=current_user,
        file_id=file_id,
        data=data,
    )

    return FileEditResponse.model_validate(edited)
