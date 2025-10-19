"""Pydantic schemas for tag deletion."""

from pydantic import BaseModel


class TagDeleteResponse(BaseModel):
    """
    Response schema for tag delete. Contains the related
    file ID and the latest revision number.
    """
    file_id: int
    latest_revision_number: int
