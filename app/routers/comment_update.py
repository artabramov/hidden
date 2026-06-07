# app/routers/comment_update.py
# SPDX-License-Identifier: SSPL-1.0

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.auth import AccessLevel, require_access
from app.dependencies.session import get_session
from app.models.user import User
from app.schemas.comment_update import (
    COMMENT_UPDATE_ERRORS,
    CommentUpdateRequest,
    CommentUpdateResponse,
)
from app.services.comment_update import update_comment

router = APIRouter(tags=["Comments"])


@router.patch(
    "/comment/{comment_id}",
    response_model=CommentUpdateResponse,
    responses=COMMENT_UPDATE_ERRORS,
    status_code=status.HTTP_200_OK,
    summary="Update file comment",
)
async def comment_update_router(
    comment_id: int,
    data: CommentUpdateRequest,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_access(AccessLevel.WRITE)),
) -> CommentUpdateResponse:
    """
    Updates an existing file comment. Only the comment creator may
    update it. The parent folder must not be write-protected.

    **Hooks:**

    `COMMENT_UPDATE_COMPLETED` — executed after the comment is
    successfully updated.

    **Authentication:**

    - Requires a valid token with write access or higher.

    **Request path:**

    - `comment_id` — ID of the target comment.

    **Request body:**

    - `CommentUpdateRequest` — updated comment body.

    **Response:**

    `CommentUpdateResponse` — updated comment ID.

    **Response codes:**

    - `200` — Comment updated successfully.
    - `401` — Invalid, expired, or missing token.
    - `403` — User inactive, blocked, or lacks writer access, or not owner.
    - `404` — Target comment was not found.
    - `422` — Input values failed validation.
    - `423` — Parent folder is write-protected.
    - `503` — Service temporarily unavailable.
    """
    comment = await update_comment(
        session=session,
        user=current_user,
        comment_id=comment_id,
        data=data,
    )

    return CommentUpdateResponse.model_validate(comment)
