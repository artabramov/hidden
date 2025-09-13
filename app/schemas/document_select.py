"""Pydantic schemas for document detail retrieval."""

from typing import Optional
from pydantic import BaseModel
from app.schemas.user_select import UserSelectResponse
from app.schemas.collection_select import CollectionSelectResponse


class DocumentSelectResponse(BaseModel):
    """
    Response schema for document detail retrieval. Includes the document
    ID; creator data; parent collection data; creation and last-update
    timestamps (Unix seconds, UTC); flagged status; filename; file size;
    MIME type; content checksum; optional summary; and the latest
    revision number."""

    id: int
    user: UserSelectResponse
    collection: CollectionSelectResponse
    created_date: int
    updated_date: int
    flagged: bool
    filename: str
    filesize: int
    mimetype: Optional[str]
    checksum: str
    summary: Optional[str]
    latest_revision: int
