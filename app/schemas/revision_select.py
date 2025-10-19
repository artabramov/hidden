"""Pydantic schemas for revision detail retrieval."""

from pydantic import BaseModel
from app.schemas.user_select import UserSelectResponse


class RevisionSelectResponse(BaseModel):
    """
    Response schema for revision retrieval. Includes the revision ID;
    creator data; parent file ID; creation timestamp (Unix seconds,
    UTC); revision number; UUID (revision file name); its file size;
    and content checksum.
    """
    id: int
    user: UserSelectResponse
    file_id: int
    created_date: int
    revision_number: int
    uuid: str
    filesize: int
    checksum: str
