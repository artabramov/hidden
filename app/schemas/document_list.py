"""Pydantic schemas for document listing."""

from typing import Optional, Literal, List
from pydantic import BaseModel, Field, ConfigDict
from app.schemas.document_select import DocumentSelectResponse


class DocumentListRequest(BaseModel):
    """
    Request schema for listing documents. Supports optional filters on
    creation time (Unix seconds, UTC), owner and collection IDs, flagged
    status, filename and MIME type (case-insensitive substring match),
    and file size (bytes); pagination via offset (default 0) and limit
    (default 50, maximum 500); and ordering by a fixed set of fields
    with order (asc, desc, or rand; default desc). Incoming strings
    are stripped; extra fields are rejected.
    """
    model_config = ConfigDict(
        str_strip_whitespace=True,
        extra="forbid",
    )

    created_date__ge: Optional[int] = Field(default=None, ge=0)
    created_date__le: Optional[int] = Field(default=None, ge=0)
    user_id__eq: Optional[int] = Field(default=None, ge=1)
    collection_id__eq: Optional[int] = Field(default=None, ge=1)
    flagged__eq: Optional[bool] = None
    filename__ilike: Optional[str] = None
    mimetype__ilike: Optional[str] = None
    filesize__ge: Optional[int] = Field(default=None, ge=0)
    filesize__le: Optional[int] = Field(default=None, ge=0)
    offset: int = Field(default=0, ge=0)
    limit: int = Field(default=50, ge=1, le=500)
    order_by: Literal[
        "id", "created_date", "updated_date", "user_id",
        "collection_id", "flagged", "filename", "filesize",
        "mimetype"] = "created_date"
    order: Literal["asc", "desc", "rand"] = "desc"


class DocumentListResponse(BaseModel):
    """
    Response schema for document listing. Contains the selected page
    of documents and the total number of matches before pagination.
    """
    documents: List[DocumentSelectResponse]
    documents_count: int = Field(ge=0)
