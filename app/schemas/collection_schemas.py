"""
The module defines Pydantic schemas for managing collections. Includes
schemas for inserting, selecting, updating, deleting, and listing
collections.
"""

from typing import Optional, Literal, List, Union
from pydantic import BaseModel, Field, field_validator
from app.filters.collection_filters import (
    filter_collection_name, filter_collection_summary)


class CollectionInsertRequest(BaseModel):
    """
    Pydantic schema for creating a new collection entity. It requires
    the collection's locked status, name, and optionally a collection
    summary.
    """
    is_locked: bool
    collection_name: str = Field(..., min_length=1, max_length=256)
    collection_summary: Optional[str] = Field(max_length=512, default=None)

    @field_validator("collection_name", mode="before")
    def filter_collection_name(cls, collection_name: str) -> str:
        return filter_collection_name(collection_name)

    @field_validator("collection_summary", mode="before")
    def filter_collection_summary(cls, collection_summary: str = None) -> Union[str, None]:  # noqa E501
        return filter_collection_summary(collection_summary)


class CollectionInsertResponse(BaseModel):
    """
    Pydantic schema for the response after creating a new collection
    entity. It includes the ID assigned to the newly created collection.
    """
    collection_id: int


class CollectionSelectResponse(BaseModel):
    """
    Pydantic schema for the response after retrieving a collection
    entity. It includes the collection's ID, creation and update dates,
    user ID, locked status, name, summary, document count, and
    associated user details.
    """
    id: int
    created_date: int
    updated_date: int
    locked_date: int
    user_id: int
    user_name: str
    is_locked: bool
    collection_name: str
    collection_summary: Optional[str] = None
    documents_count: int


class CollectionUpdateRequest(BaseModel):
    """
    Pydantic schema for updating an existing collection entity. It
    requires the locked status, collection name, and optionally a
    collection summary.
    """
    is_locked: bool
    collection_name: str = Field(..., min_length=1, max_length=256)
    collection_summary: Optional[str] = Field(max_length=512, default=None)

    @field_validator("collection_name", mode="before")
    def filter_collection_name(cls, collection_name: str) -> str:
        return filter_collection_name(collection_name)

    @field_validator("collection_summary", mode="before")
    def filter_collection_summary(cls, collection_summary: str = None) -> Union[str, None]:  # noqa E501
        return filter_collection_summary(collection_summary)


class CollectionUpdateResponse(BaseModel):
    """
    Pydantic schema for the response after updating a collection entity.
    It includes the ID assigned to the updated collection.
    """
    collection_id: int


class CollectionLockUpdateRequest(BaseModel):
    """
    Pydantic schema for updating the locked status of a collection entity.
    """
    is_locked: bool


class CollectionLockUpdateResponse(BaseModel):
    """
    Pydantic schema for the response after updating the locked status
    of a collection entity. It includes the ID assigned to the
    collection.
    """
    collection_id: int


class CollectionDeleteResponse(BaseModel):
    """
    Pydantic schema for the response after deleting a collection entity.
    It includes the ID assigned to the deleted collection.
    """
    collection_id: int


class CollectionListRequest(BaseModel):
    """
    Pydantic schema for requesting a list of collection entities. It
    allows optional filters for collection name, locked status, and
    various counts and sizes. Also includes pagination options (offset
    and limit), and ordering criteria.
    """
    user_id__eq: Optional[int] = None
    collection_name__ilike: Optional[str] = None
    is_locked__eq: Optional[bool] = None
    offset: int = Field(ge=0)
    limit: int = Field(ge=1, le=200)
    order_by: Literal[
        "id", "created_date", "updated_date", "locked_date", "is_locked",
        "user_id", "collection_name", "documents_count"]
    order: Literal["asc", "desc", "rand"]


class CollectionListResponse(BaseModel):
    """
    Pydantic schema for the response when listing collection entities.
    It includes a list of collection entities and the total count of
    collections that match the request criteria.
    """
    collections: List[CollectionSelectResponse]
    collections_count: int
