# app/routers/file_thumbnail_retrieve.py
# SPDX-License-Identifier: SSPL-1.0

from fastapi import APIRouter, Depends, status
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.auth import AccessLevel, require_access
from app.dependencies.session import get_session
from app.models.user import User
from app.schemas.file_thumbnail_retrieve import FILE_THUMBNAIL_RETRIEVE_ERRORS
from app.services.file_thumbnail_retrieve import retrieve_file_thumbnail

router = APIRouter(tags=["Files"])


@router.get(
    "/file/{file_id}/thumbnail",
    responses=FILE_THUMBNAIL_RETRIEVE_ERRORS,
    status_code=status.HTTP_200_OK,
    summary="Retrieve file thumbnail",
)
async def file_thumbnail_retrieve_router(
    file_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_access(AccessLevel.READ)),
) -> Response:
    """
    Returns the thumbnail image for the specified file.

    **Hooks:**

    `FILE_THUMBNAIL_RETRIEVE_COMPLETED` — executed after thumbnail
    metadata is retrieved from the database. Not emitted on cache hits.

    **Authentication:**

    - Requires a valid token with read access or higher.

    **Request path:**

    - `file_id` — ID of the source file.

    **Response:**

    Binary thumbnail image.

    **Response codes:**

    - `200` — Thumbnail returned successfully.
    - `401` — Invalid, expired, or missing token.
    - `403` — User inactive, blocked, or lacks read access.
    - `404` — File, thumbnail record, or thumbnail file was not found.
    - `422` — Input values failed validation.
    - `503` — Service temporarily unavailable.
    """
    mimetype, data = await retrieve_file_thumbnail(
        session=session,
        file_id=file_id,
    )

    return Response(content=data, media_type=mimetype)
