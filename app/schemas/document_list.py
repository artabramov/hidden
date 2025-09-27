"""Pydantic schemas for listing documents."""

from typing import Optional, Literal, List
from pydantic import BaseModel, Field, ConfigDict
from app.schemas.document_select import DocumentSelectResponse


class DocumentListRequest(BaseModel):
    """
    Request schema for listing documents. Allows filtering by creator,
    collection, filename/mimetype (case-insensitive), flagged status,
    creation and update time ranges, and filesize range. Supports
    pagination via offset/limit. Results can be ordered by id,
    created/updated date, creator, collection, flagged, filename,
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
    collection_id__eq: Optional[int] = Field(default=None, ge=1)
    flagged__eq: Optional[bool] = None
    filename__ilike: Optional[str] = None
    filesize__ge: Optional[int] = Field(default=None, ge=0)
    filesize__le: Optional[int] = Field(default=None, ge=0)
    mimetype__ilike: Optional[str] = None
    offset: int = Field(default=0, ge=0)
    limit: int = Field(default=50, ge=1, le=500)
    order_by: Literal[
        "id", "created_date", "updated_date", "user_id",
        "collection_id", "flagged", "filename", "filesize",
        "mimetype"] = "id"
    order: Literal["asc", "desc", "rand"] = "desc"


class DocumentListResponse(BaseModel):
    """
    Response schema for listing documents. Contains the selected page
    of documents and the total number of matches before pagination.
    """

    documents: List[DocumentSelectResponse]
    documents_count: int
