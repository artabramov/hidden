"""
This module defines Pydantic schemas for listing collections.
"""

from typing import Optional, Literal, List
from pydantic import BaseModel, Field
from app.schemas.collection_select_schema import CollectionSelectResponse
from app.config import get_config

cfg = get_config()


class CollectionListRequest(BaseModel):
    """
    Request schema for listing collections with pagination and filtering
    options. Includes an optional filter by user, pagination parameters
    like offset and limit, the field to order the results by, and the
    direction of ordering. The order direction can be ascending,
    descending, or random.
    """
    user_id__eq: Optional[int] = None
    offset: Optional[int] = Field(ge=0, default=None)
    limit: Optional[int] = Field(ge=1, default=None)
    order_by: Optional[Literal[
        "id", "user_id", "collection_name_index", "documents_count"]] = None
    order: Optional[Literal["asc", "desc", "rand"]] = None

    class Config:
        """Strips whitespaces at the beginning and end of all values."""
        str_strip_whitespace = True


class CollectionListResponse(BaseModel):
    """
    Response schema for listing collections. Contains a list of
    collections and the total count of collections available.
    """
    collections: List[CollectionSelectResponse]
    collections_count: int
