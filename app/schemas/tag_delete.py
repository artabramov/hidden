"""
The module defines Pydantic schemas for deleting a document tag.
"""

from pydantic import BaseModel


class TagDeleteResponse(BaseModel):
    """
    Response schema for tag delete. Contains the related
    document ID and the latest revision number.
    """
    document_id: int
    latest_revision_number: int
