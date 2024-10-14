"""
The module defines Pydantic schemas for managing documents. Includes
schemas for inserting, selecting, updating, deleting, and listing
documents.
"""

from typing import Optional, Literal, List, Union
from pydantic import BaseModel, Field, field_validator
from app.schemas.user_schemas import UserSelectResponse
from app.schemas.partner_schemas import PartnerSelectResponse
from app.schemas.collection_schemas import CollectionSelectResponse
from app.schemas.revision_schemas import RevisionSelectResponse
from app.validators.document_validators import (
    validate_document_summary, validate_document_name, validate_tags)


class DocumentUploadResponse(BaseModel):
    document_id: int
    revision_id: int


class DocumentReplaceResponse(BaseModel):
    document_id: int
    revision_id: int


class DocumentSelectResponse(BaseModel):
    """
    Pydantic schema for the response after retrieving a document entity.
    Includes the document ID, creation and update dates, user ID,
    collection ID, document name, summary, size, and various counts
    such as revisions, comments, downloads, and favorites. Also includes
    the document tags and the latest revision details.
    """
    id: int
    created_date: int
    updated_date: int
    user_id: int
    collection_id: Optional[int]
    partner_id: Optional[int]

    document_name: str
    document_summary: Optional[str] = None
    comments_count: int
    revisions_count: int
    revisions_size: int
    downloads_count: int

    document_tags: list
    document_user: UserSelectResponse
    document_collection: Optional[CollectionSelectResponse] = None
    document_partner: Optional[PartnerSelectResponse] = None
    latest_revision: RevisionSelectResponse


class DocumentUpdateRequest(BaseModel):
    """
    Pydantic schema for request to update an existing document entity.
    Requires the document ID and collection ID to be specified, and
    optionally the document name, summary, and tags.
    """
    collection_id: Optional[int] = None
    partner_id: Optional[int] = None
    document_name: str = Field(..., min_length=1, max_length=256)
    document_summary: Optional[str] = Field(max_length=512, default=None)
    tags: Optional[str] = Field(max_length=256, default=None)

    @field_validator("document_summary", mode="before")
    def validate_document_summary(cls, document_summary: str = None) -> Union[str, None]:  # noqa E501
        return validate_document_summary(document_summary)

    @field_validator("document_name", mode="before")
    def validate_document_name(cls, document_name: str) -> str:
        return validate_document_name(document_name)

    @field_validator("tags", mode="before")
    def validate_tags(cls, tags: str = None) -> Union[str, None]:
        return validate_tags(tags)


class DocumentUpdateResponse(BaseModel):
    """
    Pydantic schema for the response after updating a document entity.
    Includes the ID assigned to the updated document.
    """
    document_id: int
    revision_id: int


class DocumentDeleteResponse(BaseModel):
    """
    Pydantic schema for the response after updating a document entity.
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
    document_name__ilike: Optional[str] = None
    comments_count__ge: Optional[int] = None
    comments_count__le: Optional[int] = None
    revisions_count__ge: Optional[int] = None
    revisions_count__le: Optional[int] = None
    revisions_size__ge: Optional[int] = None
    revisions_size__le: Optional[int] = None
    downloads_count__ge: Optional[int] = None
    downloads_count__le: Optional[int] = None
    tag_value__eq: Optional[str] = None
    offset: int = Field(ge=0)
    limit: int = Field(ge=1, le=200)
    order_by: Literal["id", "created_date", "updated_date", "user_id",
                      "collection_id", "document_name", "comments_count",
                      "revisions_count", "revisions_size", "downloads_count"]
    order: Literal["asc", "desc", "rand"]


class DocumentListResponse(BaseModel):
    """
    Pydantic schema for the response when listing document entities.
    Includes a list of document entities and the total count of
    document that match the request criteria.
    """
    documents: List[DocumentSelectResponse]
    documents_count: int
