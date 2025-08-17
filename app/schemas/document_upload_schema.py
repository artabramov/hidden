"""
The module defines Pydantic schemas for uploading documents.
"""

from pydantic import BaseModel


class DocumentUploadResponse(BaseModel):
    """
    Response schema for a successful document upload. The schema
    contains the unique identifier of the newly uploaded document.
    """
    document_id: int
