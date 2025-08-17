"""
The module defines Pydantic schemas for moving documents between
collections.
"""

from typing import Optional
from pydantic import BaseModel


class DocumentMoveRequest(BaseModel):
    """
    Request schema for moving a document to a new collection.
    """
    collection_id: Optional[int] = None


class DocumentMoveResponse(BaseModel):
    """
    Response schema for a successful document move.
    """
    document_id: int
