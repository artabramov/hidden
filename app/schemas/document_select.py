"""Pydantic schemas for document detail retrieval."""

from typing import Optional, List
from pydantic import BaseModel
from app.schemas.user_select import UserSelectResponse
from app.schemas.collection_select import CollectionSelectResponse
from app.schemas.revision_select import RevisionSelectResponse


class DocumentSelectResponse(BaseModel):
    """
    Response schema for document details. Includes identifiers, creator,
    parent collection, creation/update timestamps, flagged status,
    filename, filesize, mimetype, checksum, optional summary, latest
    revision number, and a list of document revisions.
    """

    id: int
    user: UserSelectResponse
    collection: CollectionSelectResponse
    created_date: int
    updated_date: int
    flagged: bool
    filename: str
    filesize: int
    mimetype: Optional[str] = None
    checksum: str
    summary: Optional[str] = None
    latest_revision_number: int
    document_revisions: List[RevisionSelectResponse]
