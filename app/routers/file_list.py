# app/routers/file_list.py
# SPDX-License-Identifier: SSPL-1.0

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.auth import AccessLevel, require_access
from app.dependencies.session import get_session
from app.models.user import User
from app.schemas.file_list import (
    FILE_LIST_ERRORS,
    FileListRequest,
    FileListResponse,
    build_file_list_item_response,
)
from app.services.file_list import list_files

router = APIRouter(tags=["Files"])


@router.get(
    "/files",
    response_model=FileListResponse,
    responses=FILE_LIST_ERRORS,
    status_code=status.HTTP_200_OK,
    summary="List files",
)
async def file_list_router(
    session: AsyncSession = Depends(get_session),
    params: FileListRequest = Depends(),
    current_user: User = Depends(require_access(AccessLevel.READ)),
) -> FileListResponse:
    """
    Returns files matching the query. When folder_id__eq is set, only
    files in that folder; when omitted or null, results are not limited
    to one folder.

    **Hooks:**

    `FILE_LIST_COMPLETED` — executed after file list is retrieved.

    **Authentication:**

    - Requires a valid token with read access or higher.

    **Response:**

    `FileListResponse` — list of files with compact metadata and total
    count.

    **Response codes:**

    - `200` — File list returned successfully.
    - `401` — Invalid, expired, or missing token.
    - `403` — User inactive, blocked, or lacks read access.
    - `404` — Folder not found (when set).
    - `422` — Input values failed validation.
    - `503` — Service temporarily unavailable.
    """
    files, files_count = await list_files(
        session=session,
        params=params,
    )

    return FileListResponse(
        files=[
            build_file_list_item_response(file)
            for file in files
        ],
        files_count=files_count,
    )
