"""
The module defines Pydantic schemas for handling document deletion.
"""

from pydantic import BaseModel


class DocumentDeleteResponse(BaseModel):
    """
    Response schema for the successful deletion of a document.
    Contains the documents's unique identifier that confirms the
    deletion was applied to the specific document record.
    """
    document_id: int
