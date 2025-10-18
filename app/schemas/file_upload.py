"""Pydantic schemas for file upload."""

from pydantic import BaseModel


class FileUploadResponse(BaseModel):
    """
    Response schema for file upload. Contains the created file
    ID and the latest revision number.
    """
    file_id: int
    latest_revision_number: int
