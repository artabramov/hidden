"""
The module defines Pydantic schemas for listing tags.
"""

from pydantic import BaseModel
from typing import List
from app.config import get_config

cfg = get_config()


class TagListResponse(BaseModel):
    """
    Response schema for listing tags. Contains a list of tags.
    """
    tags: List[dict]
