"""
The module defines Pydantic schemas for managing documents. Includes
schemas for inserting, selecting, updating, deleting, and listing
documents.
"""

from typing import Optional, Literal, List, Union
from pydantic import BaseModel, Field, field_validator
from app.filters.document_filters import (
    filter_document_summary, filter_document_filename, filter_tags)


class DocumentUploadResponse(BaseModel):
    """
    Pydantic schema for the response after uploading a document.
    Includes the assigned document ID and revision ID.
    """
    document_id: int
    revision_id: int


class DocumentReplaceResponse(BaseModel):
    """
    Pydantic schema for the response after replacing an existing
    document. Includes the assigned document ID and revision ID.
    """
    document_id: int
    revision_id: int


class DocumentSelectResponse(BaseModel):
    """
    Pydantic schema for the response after retrieving a document entity.
    Includes the document ID, creation and update dates, user ID,
    collection ID, document filename, size, mimetype, summary, and tags.
    Also includes counts for comments, revisions, downloads, along with
    the latest revision ID.
    """
    id: int
    created_date: int
    updated_date: int
    user_id: int
    user_name: str
    collection_id: int
    collection_name: str
    partner_id: Optional[int]
    partner_name: Optional[str]
    latest_revision_id: int
    is_flagged: bool

    document_filename: str
    document_size: int
    document_mimetype: str
    document_summary: Optional[str] = None
    thumbnail_url: Optional[str] = None
    document_tags: list

    comments_count: int
    revisions_count: int
    downloads_count: int


class DocumentUpdateRequest(BaseModel):
    """
    Pydantic schema for request to update an existing document entity.
    Requires the document ID and collection ID to be specified, and
    optionally the document name, summary, and tags.
    """
    collection_id: int
    partner_id: Optional[int] = None
    is_flagged: bool
    document_filename: str = Field(..., min_length=1, max_length=256)
    document_summary: Optional[str] = Field(max_length=512, default=None)
    document_tags: Optional[str] = Field(max_length=256, default=None)

    @field_validator("document_filename", mode="before")
    def filter_document_filename(cls, document_filename: str) -> str:
        return filter_document_filename(document_filename)

    @field_validator("document_summary", mode="before")
    def filter_document_summary(cls, document_summary: str = None) -> Union[str, None]:  # noqa E501
        return filter_document_summary(document_summary)

    @field_validator("document_tags", mode="before")
    def filter_tags(cls, document_tags: str = None) -> Union[str, None]:
        return filter_tags(document_tags)


class DocumentUpdateResponse(BaseModel):
    """
    Pydantic schema for the response after updating a document entity.
    Includes the ID assigned to the updated document.
    """
    document_id: int
    revision_id: int


class DocumentPinRequest(BaseModel):
    """
    Pydantic schema for request to pin or unpin document entity.
    Requires the is_flagged to be specified.
    """
    is_flagged: bool


class DocumentPinResponse(BaseModel):
    """
    Pydantic schema for the response after pinning a document. Includes
    the document ID and revision ID.
    """
    document_id: int
    revision_id: int


class DocumentMoveResponse(BaseModel):
    """
    Pydantic schema for the response after moving a document to another
    collection. Includes the document ID and revision ID.
    """
    document_id: int
    revision_id: int


class DocumentDeleteResponse(BaseModel):
    """
    Pydantic schema for the response after deketubg a document entity.
    Includes the ID assigned to the deleted document.
    """
    document_id: int


class DocumentListRequest(BaseModel):
    """
    Pydantic schema for requesting a list of document entities. Requires
    pagination options with offset and limit, ordering criteria, and
    optional filters for document name and tag value.
    """
    collection_id__eq: Optional[int] = None
    partner_id__eq: Optional[int] = None
    is_flagged__eq: Optional[bool] = None
    document_filename__ilike: Optional[str] = None
    document_size__ge: Optional[int] = None
    document_size__le: Optional[int] = None
    document_mimetype__ilike: Optional[str] = None
    tag_value__eq: Optional[str] = None
    offset: int = Field(ge=0)
    limit: int = Field(ge=1, le=200)
    order_by: Literal[
        "id", "created_date", "updated_date", "user_id", "collection_id",
        "partner_id", "is_flagged", "document_filename", "document_size",
        "document_mimetype", "comments_count", "revisions_count",
        "downloads_count"]
    order: Literal["asc", "desc", "rand"]


class DocumentListResponse(BaseModel):
    """
    Pydantic schema for the response when listing document entities.
    Includes a list of document entities and the total count of
    document that match the request criteria.
    """
    documents: List[DocumentSelectResponse]
    documents_count: int
