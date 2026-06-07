# app/routers/comment_delete.py
# SPDX-License-Identifier: SSPL-1.0

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.auth import AccessLevel, require_access
from app.dependencies.session import get_session
from app.models.user import User
from app.schemas.comment_delete import (
    COMMENT_DELETE_ERRORS,
    CommentDeleteResponse,
)
from app.services.comment_delete import delete_comment

router = APIRouter(tags=["Comments"])


@router.delete(
    "/comment/{comment_id}",
    response_model=CommentDeleteResponse,
    responses=COMMENT_DELETE_ERRORS,
    status_code=status.HTTP_200_OK,
    summary="Delete file comment",
)
async def comment_delete_router(
    comment_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_access(AccessLevel.WRITE)),
) -> CommentDeleteResponse:
    """
    Deletes an existing file comment. Only the comment creator may
    delete it. The parent folder must not be write-protected.

    **Hooks:**

    `COMMENT_DELETE_COMPLETED` — executed after the comment is
    successfully deleted.

    **Authentication:**

    - Requires a valid token with write access or higher.

    **Request path:**

    - `comment_id` — ID of the target comment.

    **Response:**

    `CommentDeleteResponse` — deleted comment ID.

    **Response codes:**

    - `200` — Comment deleted successfully.
    - `401` — Invalid, expired, or missing token.
    - `403` — User inactive, blocked, lacks writer access, or not owner.
    - `404` — Target comment was not found.
    - `422` — Input values failed validation.
    - `423` — Parent folder is write-protected.
    - `503` — Service temporarily unavailable.
    """
    comment = await delete_comment(
        session=session,
        user=current_user,
        comment_id=comment_id,
    )

    return CommentDeleteResponse.model_validate(comment)
