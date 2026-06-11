# app/routers/file_tag_delete.py
# SPDX-License-Identifier: GPL-3.0-only

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.auth import AccessLevel, require_access
from app.dependencies.session import get_session
from app.models.user import User
from app.paths.file_tag import get_file_tag_path
from app.schemas.file_tag_delete import FILE_TAG_DELETE_ERRORS
from app.schemas.file_tag_path import FileTagPath
from app.services.file_tag_delete import delete_file_tag

router = APIRouter(tags=["Tags"])


@router.delete(
    "/file/{file_id}/tag/{tag}",
    responses=FILE_TAG_DELETE_ERRORS,
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete file tag",
)
async def file_tag_delete_router(
    path: FileTagPath = Depends(get_file_tag_path),
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_access(AccessLevel.EDIT)),
) -> Response:
    """
    Deletes a tag from an existing file. The operation is idempotent: if
    the file does not have the tag, no row is deleted. The parent folder
    must not be write-protected.

    **Hooks:**

    `TAG_DELETE_COMPLETED` — executed after the tag is successfully
    deleted.

    **Authentication:**

    - Requires a valid token with edit access or higher.

    **Request path:**

    - `file_id` — ID of the target file.
    - `tag` — tag value attached to the file.

    **Response:**

    Empty response body.

    **Response codes:**

    - `204` — File tag does not exist after the request.
    - `401` — Invalid, expired, or missing token.
    - `403` — User inactive, blocked, or lacks editor access.
    - `404` — Target file was not found.
    - `422` — Input values failed validation.
    - `423` — Parent folder is write-protected.
    - `503` — Service temporarily unavailable.
    """
    await delete_file_tag(
        session=session,
        path=path,
    )

    return Response(status_code=status.HTTP_204_NO_CONTENT)
