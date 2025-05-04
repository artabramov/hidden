"""
The module defines Pydantic schemas for listing settings.
"""

from pydantic import BaseModel
from app.config import get_config

cfg = get_config()


class SettingListResponse(BaseModel):
    """
    Response schema representing the response for listing all available
    settings.
    """
    settings: dict
