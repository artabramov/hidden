"""
The module defines Pydantic schemas for managing collections. Includes
schemas for inserting, selecting, updating, deleting, and listing
collections.
"""

from typing import Optional, Literal, List, Union
from pydantic import BaseModel, Field, field_validator
from app.schemas.user_schemas import UserSelectResponse
from app.validators.collection_validators import (
    validate_collection_name, validate_collection_summary)


class CollectionInsertRequest(BaseModel):
    """
    Pydantic schema for request to create a new collection entity.
    Requires the locked status, collection name, and optionally a
    collection summary to be specified.
    """
    is_locked: bool
    collection_name: str = Field(..., min_length=1, max_length=256)
    collection_summary: Optional[str] = Field(max_length=512, default=None)

    @field_validator("collection_name", mode="before")
    def validate_collection_name(cls, collection_name: str) -> str:
        return validate_collection_name(collection_name)

    @field_validator("collection_summary", mode="before")
    def validate_collection_summary(cls, collection_summary: str = None) -> Union[str, None]:  # noqa E501
        return validate_collection_summary(collection_summary)


class CollectionInsertResponse(BaseModel):
    """
    Pydantic schema for the response after creating a new collection
    entity. Includes the ID assigned to the newly created collection.
    """
    collection_id: int


class CollectionSelectResponse(BaseModel):
    """
    Pydantic schema for the response after retrieving a collection
    entity. Includes the collection ID, creation and update dates,
    user ID, locked status, collection name, collection summary,
    counts for documents and revisions, associated with the
    collection, and details of the user.
    """
    id: int
    created_date: int
    updated_date: int
    user_id: int
    is_locked: bool
    collection_name: str
    collection_summary: Optional[str] = None
    documents_count: int
    revisions_count: int
    revisions_size: int
    collection_user: UserSelectResponse


class CollectionUpdateRequest(BaseModel):
    """
    Pydantic schema for request to update an existing collection entity.
    Requires the  locked status, collection name, and optionally
    collection summary to be specified.
    """
    is_locked: bool
    collection_name: str = Field(..., min_length=1, max_length=256)
    collection_summary: Optional[str] = Field(max_length=512, default=None)

    @field_validator("collection_name", mode="before")
    def validate_collection_name(cls, collection_name: str) -> str:
        return validate_collection_name(collection_name)

    @field_validator("collection_summary", mode="before")
    def validate_collection_summary(cls, collection_summary: str = None) -> Union[str, None]:  # noqa E501
        return validate_collection_summary(collection_summary)


class CollectionUpdateResponse(BaseModel):
    """
    Pydantic schema for the response after updating a collection entity.
    Includes the ID assigned to the updated collection.
    """
    collection_id: int


class CollectionDeleteResponse(BaseModel):
    """
    Pydantic schema for the response after deleting a collection entity.
    Includes the ID assigned to the deleted collection.
    """
    collection_id: int


class CollectionListRequest(BaseModel):
    """
    Pydantic schema for requesting a list of collection entities.
    Requires optional filters for collection name, locked status, and
    various counts and sizes. Also includes pagination options with
    offset and limit, and ordering criteria.
    """
    collection_name__ilike: Optional[str] = None
    is_locked__eq: Optional[bool] = None
    documents_count__ge: Optional[int] = None
    documents_count__le: Optional[int] = None
    revisions_count__ge: Optional[int] = None
    revisions_count__le: Optional[int] = None
    revisions_size__ge: Optional[int] = None
    revisions_size__le: Optional[int] = None
    offset: int = Field(ge=0)
    limit: int = Field(ge=1, le=200)
    order_by: Literal["id", "created_date", "updated_date", "user_id",
                      "collection_name", "documents_count", "revisions_count",
                      "revisions_size"]
    order: Literal["asc", "desc", "rand"]


class CollectionListResponse(BaseModel):
    """
    Pydantic schema for the response when listing collection entities.
    Includes a list of collection entities and the total count of
    collections that match the request criteria.
    """
    collections: List[CollectionSelectResponse]
    collections_count: int
