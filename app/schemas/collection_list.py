"""Pydantic schemas for collection listing."""

from typing import Optional, Literal, List
from pydantic import BaseModel, Field, ConfigDict
from app.schemas.collection_select import CollectionSelectResponse


class CollectionListRequest(BaseModel):
    """
    Request schema for listing collections with filtering, pagination,
    and ordering.
    """
    model_config = ConfigDict(
        str_strip_whitespace=True,
        extra="forbid",
    )

    user_id__eq: Optional[int] = Field(default=None, ge=1)
    created_date__ge: Optional[int] = Field(default=None, ge=0)
    created_date__le: Optional[int] = Field(default=None, ge=0)
    readonly__eq: Optional[bool] = None
    name__ilike: Optional[str] = None
    offset: int = Field(default=0, ge=0)
    limit: int = Field(default=50, ge=1, le=500)
    order_by: Literal[
        "id", "created_date", "updated_date", "user_id",
        "readonly", "name", "filesize"] = "created_date"
    order: Literal["asc", "desc", "rand"] = "desc"


class CollectionListResponse(BaseModel):
    """
    Response schema for collection listing. Contains the selected page
    of collections and the total number of matches before pagination.
    """
    collections: List[CollectionSelectResponse]
    collections_count: int = Field(ge=0)
