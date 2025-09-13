"""Pydantic schemas for collection detail retrieval."""

from typing import Optional, List
from pydantic import BaseModel
from app.schemas.user_select import UserSelectResponse


class CollectionSelectResponse(BaseModel):
    """
    Response schema for collection detail retrieval. Includes the
    collection ID; creation and last-update timestamps (Unix seconds,
    UTC); creator; read-only flag; normalized name; and an optional
    summary.
    """
    id: int
    user: UserSelectResponse
    created_date: int
    updated_date: int
    readonly: bool
    name: str
    summary: Optional[str]
