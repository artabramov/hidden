"""Pydantic schemas for listing folders."""

from typing import Optional, Literal, List
from pydantic import BaseModel, Field, ConfigDict
from app.schemas.folder_select import FolderSelectResponse


class FolderListRequest(BaseModel):
    """
    Request schema for listing folders. Allows filtering by creator,
    name (case-insensitive), read-only status, and creation/update time
    ranges. Supports pagination via offset/limit. Results can be ordered
    by id, created/updated date, creator, read-only flag, name, or
    filesize, in ascending, descending, or random order. Extra fields
    are forbidden.
    """
    model_config = ConfigDict(
        str_strip_whitespace=True,
    )

    user_id__eq: Optional[int] = Field(default=None, ge=1)
    created_date__ge: Optional[int] = Field(default=None, ge=0)
    created_date__le: Optional[int] = Field(default=None, ge=0)
    updated_date__ge: Optional[int] = Field(default=None, ge=0)
    updated_date__le: Optional[int] = Field(default=None, ge=0)
    readonly__eq: Optional[bool] = None
    name__ilike: Optional[str] = None
    offset: int = Field(default=0, ge=0)
    limit: int = Field(default=50, ge=1, le=500)
    order_by: Literal[
        "id", "created_date", "updated_date", "user_id",
        "readonly", "name"] = "id"
    order: Literal["asc", "desc", "rand"] = "desc"


class FolderListResponse(BaseModel):
    """
    Response schema for listing folders. Contains the selected page
    of folders and the total number of matches before pagination.
    """
    folders: List[FolderSelectResponse]
    folders_count: int
