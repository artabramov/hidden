"""Pydantic schemas for folder deletion."""

from pydantic import BaseModel


class FolderDeleteResponse(BaseModel):
    """
    Response schema for folder deletion. Contains the deleted
    folder ID.
    """
    folder_id: int
