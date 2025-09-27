"""Pydantic schemas for document deletion."""

from pydantic import BaseModel


class DocumentDeleteResponse(BaseModel):
    """
    Response schema for document deletion. Contains the deleted
    document ID and the latest revision number.
    """

    document_id: int
    latest_revision_number: int
