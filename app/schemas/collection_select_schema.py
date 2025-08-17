"""
The module defines Pydantic schemas for selecting and retrieving the
details of a collection.
"""

from typing import Optional
from pydantic import BaseModel


class CollectionSelectResponse(BaseModel):
    """
    Response schema for selecting a collection's details. It includes
    the collection's ID, creation and update dates, user ID and username,
    collection name and summary.
    """
    id: int
    created_date: int
    updated_date: int
    user_id: int
    username: str
    collection_name: str
    collection_summary: Optional[str] = None
    thumbnail_filename: Optional[str] = None
    documents_count: int
    collection_meta: dict
