# app/routers/file_upload.py
# SPDX-License-Identifier: GPL-3.0-only

from fastapi import APIRouter, Depends
from fastapi import File as FileParam
from fastapi import UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.auth import AccessLevel, require_access
from app.dependencies.session import get_session
from app.models.user import User
from app.schemas.file_upload import (
    FILE_UPLOAD_ERRORS,
    FileUploadResponse,
)
from app.services.file_upload import upload_file

router = APIRouter(tags=["Files"])


@router.post(
    "/folder/{folder_id}/file",
    response_model=FileUploadResponse,
    responses=FILE_UPLOAD_ERRORS,
    status_code=status.HTTP_201_CREATED,
    summary="Upload file",
)
async def file_upload_router(
    folder_id: int,
    file: UploadFile = FileParam(...),
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_access(AccessLevel.WRITE)),
) -> FileUploadResponse:
    """
    Uploads a file into an existing folder.

    **Hooks:**

    `FILE_UPLOAD_COMPLETED` — executed after the file is successfully
    uploaded.

    **Authentication:**

    - Requires a valid token with write access or higher.

    **Request path:**

    - `folder_id` — ID of the target folder.

    **Request body:**

    - `multipart/form-data` with a single `file` field.

    **Response:**

    `FileUploadResponse` — uploaded file ID.

    **Response codes:**

    - `201` — File uploaded successfully.
    - `401` — Invalid, expired, or missing token.
    - `403` — User inactive, blocked, or lacks writer access.
    - `404` — Target folder was not found.
    - `409` — File conflict.
    - `422` — Input values failed validation.
    - `423` — Target folder is write-protected.
    - `503` — Service temporarily unavailable.
    """
    uploaded = await upload_file(
        session=session,
        user=current_user,
        folder_id=folder_id,
        uploaded_file=file,
    )
    return FileUploadResponse.model_validate(uploaded)
