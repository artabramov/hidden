"""
The module defines Pydantic schemas for managing document revisions.
Includes schemas for selecting, listing, and retrieving details of
document revisions. These schemas support pagination, ordering, and
filtering to retrieve specific revisions pased on criteria such as
document ID, revision creation date, and other properties.
"""

from typing import Optional, Literal, List
from pydantic import BaseModel, Field


class RevisionSelectResponse(BaseModel):
    """
    Pydantic schema for the response after retrieving a specific
    revision entity. Includes the revision ID, creation date, associated
    user and document IDs, revision filename, size, mimetype, and an
    optional thumbnail URL.
    """
    id: int
    created_date: int
    user_id: int
    user_name: str
    document_id: int
    revision_filename: str
    revision_size: int
    revision_mimetype: str
    thumbnail_url: Optional[str]


class DocumentRevisionsRequest(BaseModel):
    """
    Pydantic schema for requesting a list of document revisions.
    Includes optional filters for document ID and pagination options
    (offset and limit), along with ordering criteria (field and
    direction).
    """
    offset: int = Field(ge=0)
    limit: int = Field(ge=1, le=200)
    order_by: Literal["id", "created_date"]
    order: Literal["asc", "desc"]


class DocumentRevisionsResponse(BaseModel):
    """
    Pydantic schema for the response when listing document revisions.
    Includes a list of revision entities and the total count of
    revisions  that match the specified criteria.
    """
    revisions: List[RevisionSelectResponse]
    revisions_count: int
