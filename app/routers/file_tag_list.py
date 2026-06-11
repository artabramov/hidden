# app/routers/file_tag_list.py
# SPDX-License-Identifier: GPL-3.0-only

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.auth import AccessLevel, require_access
from app.dependencies.session import get_session
from app.models.user import User
from app.schemas.file_tag_list import (
    TAG_LIST_ERRORS,
    TagListItemResponse,
    TagListRequest,
)
from app.services.file_tag_list import list_tags

router = APIRouter(tags=["Tags"])


@router.get(
    "/tags",
    response_model=list[TagListItemResponse],
    responses=TAG_LIST_ERRORS,
    status_code=status.HTTP_200_OK,
    summary="List tags",
)
async def tag_list_router(
    session: AsyncSession = Depends(get_session),
    params: TagListRequest = Depends(),
    current_user: User = Depends(require_access(AccessLevel.READ)),
) -> list[TagListItemResponse]:
    """
    Returns the most frequently used tags across all files, ordered
    by usage count descending.

    **Authentication:**

    - Requires a valid token with read access or higher.

    **Response:**

    Array of tag objects with usage counts, ordered by usage count
    descending.

    **Response codes:**

    - `200` — Tag list returned successfully.
    - `401` — Invalid, expired, or missing token.
    - `403` — User inactive, blocked, or lacks read access.
    - `422` — Input values failed validation.
    - `503` — Service temporarily unavailable.
    """
    tags = await list_tags(
        session=session,
        params=params,
    )

    return [
        TagListItemResponse(tag=tag, usage_count=usage_count)
        for tag, usage_count in tags
    ]
