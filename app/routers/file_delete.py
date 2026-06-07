# app/routers/file_delete.py
# SPDX-License-Identifier: SSPL-1.0

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.auth import AccessLevel, require_access
from app.dependencies.session import get_session
from app.models.user import User
from app.schemas.file_delete import FILE_DELETE_ERRORS
from app.services.file_delete import delete_file

router = APIRouter(tags=["Files"])


@router.delete(
    "/file/{file_id}",
    responses=FILE_DELETE_ERRORS,
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete file",
)
async def file_delete_router(
    file_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_access(AccessLevel.ADMIN)),
) -> Response:
    """
    Deletes an existing file together with its thumbnail, revisions,
    tags, and comments. The parent folder must not be write-protected.

    **Hooks:**

    `FILE_DELETE_COMPLETED` — executed after the file is successfully
    deleted.

    **Authentication:**

    - Requires a valid token with admin access.

    **Request path:**

    - `file_id` — ID of the target file.

    **Response:**

    Empty response body.

    **Response codes:**

    - `204` — File deleted successfully.
    - `401` — Invalid, expired, or missing token.
    - `403` — User inactive, blocked, or lacks admin access.
    - `404` — Target file was not found.
    - `422` — Input values failed validation.
    - `423` — Parent folder is write-protected.
    - `503` — Service temporarily unavailable.
    """
    await delete_file(
        session=session,
        file_id=file_id,
    )

    return Response(status_code=status.HTTP_204_NO_CONTENT)
