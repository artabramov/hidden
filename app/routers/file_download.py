# app/routers/file_download.py
# SPDX-License-Identifier: SSPL-1.0

from fastapi import APIRouter, Depends, status
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.auth import AccessLevel, require_access
from app.dependencies.session import get_session
from app.models.user import User
from app.schemas.file_download import FILE_DOWNLOAD_ERRORS
from app.services.file_download import download_file

router = APIRouter(tags=["Files"])


# TODO: Signed sharing links — anonymous, time-limited, scoped access
# to a file for users without an account.


@router.get(
    "/file/{file_id}/revision/{revision_number}",
    response_class=FileResponse,
    responses=FILE_DOWNLOAD_ERRORS,
    status_code=status.HTTP_200_OK,
    summary="Download file revision",
)
async def file_download_router(
    file_id: int,
    revision_number: int,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_access(AccessLevel.READ)),
) -> FileResponse:
    """
    Downloads the specified revision of a file.

    **Hooks:**

    `FILE_DOWNLOAD_COMPLETED` — executed after revision metadata is
    retrieved.

    **Authentication:**

    - Requires a valid token with read access or higher.

    **Request path:**

    - `file_id` — ID of the file.
    - `revision_number` — Revision number to download. Use `0` for the
      current version (HEAD). Values `1` and above refer to historical
      revisions.

    **Response:**

    Binary file content.

    **Response codes:**

    - `200` — File revision returned successfully.
    - `401` — Invalid, expired, or missing token.
    - `403` — User inactive, blocked, or lacks read access.
    - `404` — File or revision record, or file on disk was not found.
    - `422` — Input values failed validation.
    - `503` — Service temporarily unavailable.
    """
    revision, file_path = await download_file(
        session=session,
        file_id=file_id,
        revision_number=revision_number,
    )

    return FileResponse(
        path=file_path,
        media_type=revision.mimetype,
        filename=revision.filename,
    )
