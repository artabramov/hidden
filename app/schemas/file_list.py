# app/schemas/file_list.py
# SPDX-License-Identifier: GPL-3.0-only

from types import SimpleNamespace
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from app.models.file import File, FileType
from app.schemas.file_select import FileSelectUserResponse
from app.schemas.pydantic_error import PydanticErrorResponse

OrderByField = Literal[
    "id",
    "created_at",
    "updated_at",
    "is_starred",
    "filename",
    "filesize",
    "mimetype",
    "comments_count",
    "latest_revision_number",
]


FILE_LIST_ERRORS = {
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
        "description": (
            "Folder was not found (only when folder_id__eq is set)."
        ),
    },
    422: {
        "model": PydanticErrorResponse,
        "description": (
            "Input values failed validation (invalid folder filter, "
            "invalid filtering values, invalid ordering values, or "
            "invalid offset / limit)."
        ),
    },
    503: {
        "description": (
            "Service is temporarily unavailable (lockdown mode enabled "
            "or gocryptfs storage not ready)."
        ),
    },
}


class FileListRequest(BaseModel):
    """
    Request schema for querying files with optional folder scope,
    filtering by metadata, pagination, and ordering. When
    folder_id__eq is omitted or null, results are not restricted to
    a single folder (global listing / search). Extra fields are
    forbidden. Leading and trailing whitespace is stripped from string
    fields.
    """

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )

    folder_id__eq: int | None = Field(
        default=None,
        ge=1,
        description=(
            "When set, list only files in this folder. When omitted or "
            "null, do not filter by folder (cross-folder listing)."
        ),
    )

    created_at__ge: int | None = Field(
        default=None,
        ge=0,
        description="Lower bound for file creation timestamp.",
    )

    created_at__le: int | None = Field(
        default=None,
        ge=0,
        description="Upper bound for file creation timestamp.",
    )

    updated_at__ge: int | None = Field(
        default=None,
        ge=0,
        description="Lower bound for file update timestamp.",
    )

    updated_at__le: int | None = Field(
        default=None,
        ge=0,
        description="Upper bound for file update timestamp.",
    )

    is_starred__eq: bool | None = Field(
        default=None,
        description="Filter by starred state.",
    )

    filename__ilike: str | None = Field(
        default=None,
        description="Case-insensitive substring match for file name.",
    )

    mimetype__ilike: str | None = Field(
        default=None,
        description="Case-insensitive substring match for MIME type.",
    )

    tag__eq: str | None = Field(
        default=None,
        description=(
            "Exact match for a tag attached to the file. Returns files "
            "that have at least one tag equal to this value."
        ),
    )

    offset: int = Field(
        default=0,
        ge=0,
        description="Number of records to skip for pagination.",
    )

    limit: int = Field(
        default=50,
        ge=1,
        le=500,
        description="Maximum number of records to return.",
    )

    order_by: OrderByField = Field(
        default="filename",
        description="Field used for result ordering.",
    )

    order: Literal["asc", "desc", "rand"] = Field(
        default="asc",
        description="Ordering direction or random ordering.",
    )


class FileListItemResponse(BaseModel):
    """
    Response schema for one file item in file listing.
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


class FileListResponse(BaseModel):
    """
    Response schema for file listing containing matched files and the
    total number of files satisfying the query conditions.
    """

    model_config = ConfigDict(
        extra="forbid",
    )

    files: list[FileListItemResponse] = Field(
        description="List of files matching the query.",
    )

    files_count: int = Field(
        ge=0,
        description="Total number of files matching the query.",
    )


def build_file_list_item_response(file: File) -> FileListItemResponse:
    """
    Build file list item response.
    """
    return FileListItemResponse.model_validate(
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
        )
    )
