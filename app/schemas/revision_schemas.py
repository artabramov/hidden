"""
The module defines Pydantic schemas for managing documents. Includes
schemas for inserting, selecting, updating, deleting, and listing
documents.
"""

from typing import Optional, Literal, List
from pydantic import BaseModel, Field
from app.schemas.user_schemas import UserSelectResponse


class RevisionSelectResponse(BaseModel):
    id: int
    created_date: int
    user_id: int
    document_id: int
    revision_size: int
    original_filename: str
    original_size: int
    original_mimetype: str
    thumbnail_url: Optional[str] = None
    downloads_count: int
    revision_user: UserSelectResponse


class RevisionListRequest(BaseModel):
    """
    Pydantic schema for requesting a list of revision entities. Includes
    optional filter for document ID and pagination options with offset
    and limit, and ordering criteria.
    """
    offset: int = Field(ge=0)
    limit: int = Field(ge=1, le=200)
    order_by: Literal["id", "created_date"]
    order: Literal["asc", "desc"]


class RevisionListResponse(BaseModel):
    """
    Pydantic schema for the response when listing revision entities.
    Includes a list of revision entities and the total count of
    revisions that match the request criteria.
    """
    revisions: List[RevisionSelectResponse]
    revisions_count: int
