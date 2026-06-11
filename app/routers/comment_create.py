# app/routers/comment_create.py
# SPDX-License-Identifier: GPL-3.0-only

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.auth import AccessLevel, require_access
from app.dependencies.session import get_session
from app.models.user import User
from app.schemas.comment_create import (
    COMMENT_CREATE_ERRORS,
    CommentCreateRequest,
    CommentCreateResponse,
)
from app.services.comment_create import create_comment

router = APIRouter(tags=["Comments"])


@router.post(
    "/file/{file_id}/comment",
    response_model=CommentCreateResponse,
    responses=COMMENT_CREATE_ERRORS,
    status_code=status.HTTP_201_CREATED,
    summary="Create file comment",
)
async def comment_create_router(
    file_id: int,
    data: CommentCreateRequest,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_access(AccessLevel.WRITE)),
) -> CommentCreateResponse:
    """
    Creates a new comment for an existing file. The file must exist and
    its parent folder must not be write-protected.

    **Hooks:**

    `COMMENT_CREATE_COMPLETED` — executed after the comment is
    successfully created.

    **Authentication:**

    - Requires a valid token with write access or higher.

    **Request path:**

    - `file_id` — ID of the target file.

    **Request body:**

    - `CommentCreateRequest` — comment body.

    **Response:**

    `CommentCreateResponse` — created comment ID.

    **Response codes:**

    - `201` — Comment created successfully.
    - `401` — Invalid, expired, or missing token.
    - `403` — User inactive, blocked, or lacks writer access.
    - `404` — Target file was not found.
    - `422` — Input values failed validation.
    - `423` — Parent folder is write-protected.
    - `503` — Service temporarily unavailable.
    """
    comment = await create_comment(
        session=session,
        user=current_user,
        file_id=file_id,
        data=data,
    )
    return CommentCreateResponse.model_validate(comment)
