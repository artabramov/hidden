"""Pydantic schemas for collection detail retrieval."""

from typing import Optional
from pydantic import BaseModel
from app.schemas.user_select import UserSelectResponse


class CollectionSelectResponse(BaseModel):
    """
    Response schema for collection detail retrieval. Includes the
    collection ID; creation and last-update timestamps (Unix seconds,
    UTC); read-only flag; collection name; optional summary; and
    creator details.
    """

    id: int
    created_date: int
    updated_date: int
    readonly: bool
    name: str
    summary: Optional[str] = None
    user: UserSelectResponse
