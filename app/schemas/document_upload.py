"""Pydantic schemas for file upload."""

from pydantic import BaseModel


class DocumentUploadResponse(BaseModel):
    """
    Response schema for file upload. Contains the created document
    ID and the latest revision number.
    """

    document_id: int
    latest_revision_number: int
