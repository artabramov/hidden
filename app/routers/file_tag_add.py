# app/routers/file_tag_add.py
# SPDX-License-Identifier: GPL-3.0-only

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.auth import AccessLevel, require_access
from app.dependencies.session import get_session
from app.models.user import User
from app.schemas.file_tag_add import (
    FILE_TAG_ADD_ERRORS,
    FileTagAddRequest,
)
from app.services.file_tag_add import add_file_tag

router = APIRouter(tags=["Tags"])


@router.post(
    "/file/{file_id}/tag",
    responses=FILE_TAG_ADD_ERRORS,
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Add file tag",
)
async def file_tag_add_router(
    file_id: int,
    data: FileTagAddRequest,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_access(AccessLevel.EDIT)),
) -> Response:
    """
    Adds a tag to an existing file. The operation is idempotent: if the
    file already has the tag, no new row is created. The parent folder
    must not be write-protected.

    **Hooks:**

    `TAG_ADD_COMPLETED` — executed after the tag is successfully added.

    **Authentication:**

    - Requires a valid token with edit access or higher.

    **Request path:**

    - `file_id` — ID of the target file.

    **Request body:**

    - `FileTagAddRequest` — tag value.

    **Response:**

    Empty response body.

    **Response codes:**

    - `204` — File tag exists after the request.
    - `401` — Invalid, expired, or missing token.
    - `403` — User inactive, blocked, or lacks editor access.
    - `404` — Target file was not found.
    - `422` — Input values failed validation.
    - `423` — Parent folder is write-protected.
    - `503` — Service temporarily unavailable.
    """
    await add_file_tag(
        session=session,
        user=current_user,
        file_id=file_id,
        data=data,
    )

    return Response(status_code=status.HTTP_204_NO_CONTENT)
