"""Pydantic schemas for listing files."""

from typing import Optional, Literal, List
from pydantic import BaseModel, Field, ConfigDict
from app.schemas.file_select import FileSelectResponse


class FileListRequest(BaseModel):
    """
    Request schema for listing files. Allows filtering by creator,
    folder, filename/mimetype (case-insensitive), flagged status,
    creation and update time ranges, filesize range, MIME type, tag
    value. Supports pagination via offset/limit. Results can be ordered
    by id, created/updated date, creator, folder, flagged, filename,
    filesize, or mimetype, in ascending, descending, or random order.
    Extra fields are forbidden.
    """

    model_config = ConfigDict(
        str_strip_whitespace=True,
    )

    created_date__ge: Optional[int] = Field(default=None, ge=0)
    created_date__le: Optional[int] = Field(default=None, ge=0)
    updated_date__ge: Optional[int] = Field(default=None, ge=0)
    updated_date__le: Optional[int] = Field(default=None, ge=0)
    user_id__eq: Optional[int] = Field(default=None, ge=1)
    folder_id__eq: Optional[int] = Field(default=None, ge=1)
    flagged__eq: Optional[bool] = None
    filename__ilike: Optional[str] = None
    filesize__ge: Optional[int] = Field(default=None, ge=0)
    filesize__le: Optional[int] = Field(default=None, ge=0)
    mimetype__ilike: Optional[str] = None
    tag_value__eq: Optional[str] = None
    offset: int = Field(default=0, ge=0)
    limit: int = Field(default=50, ge=1, le=500)
    order_by: Literal[
        "id", "created_date", "updated_date", "user_id",
        "folder_id", "flagged", "filename", "filesize",
        "mimetype"] = "id"
    order: Literal["asc", "desc", "rand"] = "desc"


class FileListResponse(BaseModel):
    """
    Response schema for listing files. Contains the selected page
    of files and the total number of matches before pagination.
    """

    files: List[FileSelectResponse]
    files_count: int
