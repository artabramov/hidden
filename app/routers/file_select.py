# app/routers/file_select.py
# SPDX-License-Identifier: GPL-3.0-only

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.auth import AccessLevel, require_access
from app.dependencies.session import get_session
from app.models.user import User
from app.schemas.file_select import (
    FILE_SELECT_ERRORS,
    FileSelectResponse,
    build_file_response,
)
from app.services.file_select import select_file

router = APIRouter(tags=["Files"])


@router.get(
    "/file/{file_id}",
    response_model=FileSelectResponse,
    responses=FILE_SELECT_ERRORS,
    status_code=status.HTTP_200_OK,
    summary="Select file by ID",
)
async def file_select_router(
    file_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_access(AccessLevel.READ)),
) -> FileSelectResponse:
    """
    Returns file metadata for the specified file identifier.

    **Hooks:**

    `FILE_SELECT_COMPLETED` — executed after file data is retrieved.

    **Authentication:**

    - Requires a valid token with read access or higher.

    **Request path:**

    - `file_id` — ID of the file to retrieve.

    **Response:**

    `FileSelectResponse` — identifier, parent folder ID, filename,
    summary, tags, thumbnail state, comments, revisions, checksum,
    size, MIME type, and creation / update metadata.

    **Response codes:**

    - `200` — File data returned successfully.
    - `401` — Invalid, expired, or missing token.
    - `403` — User inactive, blocked, or lacks read access.
    - `404` — File not found.
    - `422` — Input values failed validation.
    - `503` — Service temporarily unavailable.
    """
    file = await select_file(
        session=session,
        file_id=file_id,
    )

    return build_file_response(file)
