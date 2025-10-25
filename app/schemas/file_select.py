"""Pydantic schemas for file detail retrieval."""

from typing import Optional, List
from pydantic import BaseModel
from app.schemas.user_select import UserSelectResponse
from app.schemas.folder_select import FolderSelectResponse
from app.schemas.revision_select import RevisionSelectResponse


class FileSelectResponse(BaseModel):
    """
    Response schema for file details. Includes identifiers, creator,
    parent folder, creation/update timestamps, flagged status, filename,
    filesize, mimetype, checksum, optional summary, latest revision
    number, and a list of file revisions.
    """
    id: int
    user: UserSelectResponse
    folder: FolderSelectResponse
    created_date: int
    updated_date: int
    flagged: bool
    filename: str
    filesize: int
    mimetype: Optional[str] = None
    checksum: str
    summary: Optional[str] = None
    latest_revision_number: int
    has_thumbnail: bool
    file_revisions: List[RevisionSelectResponse]
    file_tags: list = None
