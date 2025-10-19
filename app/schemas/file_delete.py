"""Pydantic schemas for file deletion."""

from pydantic import BaseModel


class FileDeleteResponse(BaseModel):
    """
    Response schema for file deletion. Contains the deleted file ID
    and the latest revision number.
    """
    file_id: int
    latest_revision_number: int
