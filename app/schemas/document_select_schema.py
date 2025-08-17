"""
The module defines Pydantic schemas for selecting a document's details.
"""

from typing import Optional, List
from pydantic import BaseModel


class DocumentSelectResponse(BaseModel):
    """
    Response schema for selecting a documents's details. This schema
    includes comprehensive information about the document, such as its
    ID, creation and update dates, user details, document's metadata,
    collection info, and file details.
    """
    id: int
    created_date: int
    updated_date: int
    user_id: int
    username: str
    collection_id: Optional[int]
    collection_name: Optional[str]
    original_filename: str
    document_filesize: int
    document_mimetype: str
    document_summary: Optional[str]
    document_tags: List[str]
    thumbnail_filename: Optional[str]
    document_meta: dict
