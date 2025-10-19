"""Pydantic schemas for folder detail retrieval."""

from typing import Optional
from pydantic import BaseModel
from app.schemas.user_select import UserSelectResponse


class FolderSelectResponse(BaseModel):
    """
    Response schema for folder detail retrieval. Includes the
    folder ID; creation and last-update timestamps (Unix seconds,
    UTC); read-only flag; folder name; optional summary; and
    creator details.
    """
    id: int
    created_date: int
    updated_date: int
    readonly: bool
    name: str
    summary: Optional[str] = None
    user: UserSelectResponse
