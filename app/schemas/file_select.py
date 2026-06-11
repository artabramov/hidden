# app/schemas/file_select.py
# SPDX-License-Identifier: GPL-3.0-only

from types import SimpleNamespace

from pydantic import BaseModel, ConfigDict, Field

from app.models.file import File, FileType
from app.schemas.pydantic_error import PydanticErrorResponse

FILE_SELECT_ERRORS = {
    401: {
        "description": (
            "Invalid, expired, or missing authentication token."
        ),
    },
    403: {
        "description": (
            "Authenticated user is inactive, blocked, or lacks "
            "required permissions."
        ),
    },
    404: {
        "description": "Target file was not found.",
    },
    422: {
        "model": PydanticErrorResponse,
        "description": "Input values failed validation (invalid file ID).",
    },
    503: {
        "description": (
            "Service is temporarily unavailable (lockdown mode enabled "
            "or gocryptfs storage not ready)."
        ),
    },
}


class FileSelectUserResponse(BaseModel):
    """
    Response schema for user reference.
    """

    model_config = ConfigDict(
        extra="forbid",
        from_attributes=True,
        populate_by_name=True,
    )

    user_id: int = Field(
        validation_alias="id",
        description="Identifier of the user.",
    )

    display_name: str = Field(
        description="Display name of the user.",
    )


class FileSelectCommentResponse(BaseModel):
    """
    Response schema for file comment metadata.
    """

    model_config = ConfigDict(
        extra="forbid",
        from_attributes=True,
        populate_by_name=True,
    )

    comment_id: int = Field(
        validation_alias="id",
        description="Identifier of the file comment.",
    )

    created_by: FileSelectUserResponse = Field(
        description="User who created the comment.",
    )

    created_at: int = Field(
        description="Timestamp when the comment was created.",
    )

    updated_at: int | None = Field(
        default=None,
        description="Timestamp when the comment was last updated.",
    )

    body: str = Field(
        description="Comment body.",
    )


class FileSelectRevisionResponse(BaseModel):
    """
    Response schema for file revision metadata.
    """

    model_config = ConfigDict(
        extra="forbid",
        from_attributes=True,
        populate_by_name=True,
    )

    revision_id: int = Field(
        validation_alias="id",
        description="Identifier of the file revision.",
    )

    revision_number: int = Field(
        ge=1,
        description="File revision number.",
    )

    created_by: FileSelectUserResponse = Field(
        description="User who created the file revision.",
    )

    created_at: int = Field(
        description="Timestamp when the revision was created.",
    )

    filesize: int = Field(
        ge=0,
        description="Revision file size in bytes.",
    )

    mimetype: str | None = Field(
        default=None,
        description="Revision MIME type.",
    )

    checksum: str = Field(
        description="Revision checksum.",
    )


class FileSelectResponse(BaseModel):
    """
    Response schema for file selection containing file metadata,
    tags, thumbnail state, comments, and revisions.
    """

    model_config = ConfigDict(
        extra="forbid",
        from_attributes=True,
        populate_by_name=True,
    )

    file_id: int = Field(
        validation_alias="id",
        description="Identifier of the file.",
    )

    folder_id: int = Field(
        description="Identifier of the parent folder.",
    )

    created_by: FileSelectUserResponse = Field(
        description="User who uploaded the file.",
    )

    created_at: int = Field(
        description="Timestamp when the file was created.",
    )

    updated_by: FileSelectUserResponse | None = Field(
        default=None,
        description="User who updated the file last time.",
    )

    updated_at: int | None = Field(
        default=None,
        description="Timestamp when the file was last updated.",
    )

    is_starred: bool = Field(
        description="Whether the file is starred.",
    )

    filename: str = Field(
        description="File name.",
    )

    filesize: int = Field(
        ge=0,
        description="File size in bytes.",
    )

    mimetype: str | None = Field(
        default=None,
        description="File MIME type.",
    )

    checksum: str = Field(
        description="File checksum.",
    )

    summary: str | None = Field(
        default=None,
        description="Optional file summary.",
    )

    comments_count: int = Field(
        ge=0,
        description="Number of comments attached to the file.",
    )

    latest_revision_number: int = Field(
        ge=0,
        description="Latest file revision number.",
    )

    file_tags: list[str] = Field(
        description="Tags attached to the file.",
    )

    has_thumbnail: bool = Field(
        description="Whether the file has an associated thumbnail.",
    )

    filetype: FileType = Field(
        description="File type derived from MIME type.",
    )

    file_comments: list[FileSelectCommentResponse] = Field(
        description="Comments attached to the file.",
    )

    file_revisions: list[FileSelectRevisionResponse] = Field(
        description="File revision history.",
    )


def build_file_response(file: File) -> FileSelectResponse:
    """
    Build file selection response.
    """
    return FileSelectResponse.model_validate(
        SimpleNamespace(
            id=file.id,
            folder_id=file.folder_id,
            created_by=SimpleNamespace(
                id=file.file_created_by_user.id,
                display_name=file.file_created_by_user.display_name,
            ),
            created_at=file.created_at,
            updated_by=(
                SimpleNamespace(
                    id=file.file_updated_by_user.id,
                    display_name=file.file_updated_by_user.display_name,
                )
                if file.file_updated_by_user is not None
                else None
            ),
            updated_at=file.updated_at,
            is_starred=file.is_starred,
            filename=file.filename,
            filesize=file.filesize,
            mimetype=file.mimetype,
            checksum=file.checksum,
            summary=file.summary,
            comments_count=file.comments_count,
            latest_revision_number=file.latest_revision_number,
            file_tags=[file_tag.tag for file_tag in file.file_tags],
            has_thumbnail=file.has_thumbnail,
            filetype=file.filetype,
            file_comments=[
                SimpleNamespace(
                    id=comment.id,
                    created_by=SimpleNamespace(
                        id=comment.comment_created_by_user.id,
                        display_name=(
                            comment.comment_created_by_user.display_name
                        ),
                    ),
                    created_at=comment.created_at,
                    updated_at=comment.updated_at,
                    body=comment.body,
                )
                for comment in file.file_comments
            ],
            file_revisions=[
                SimpleNamespace(
                    id=revision.id,
                    revision_number=revision.revision_number,
                    created_by=SimpleNamespace(
                        id=revision.revision_created_by_user.id,
                        display_name=(
                            revision.revision_created_by_user.display_name
                        ),
                    ),
                    created_at=revision.created_at,
                    filesize=revision.filesize,
                    mimetype=revision.mimetype,
                    checksum=revision.checksum,
                )
                for revision in file.file_revisions
            ],
        )
    )
