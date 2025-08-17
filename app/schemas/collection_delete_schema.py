"""
This module defines Pydantic schemas for handling the deletion of a
collection.
"""

from pydantic import BaseModel


class CollectionDeleteResponse(BaseModel):
    """
    Response schema for the successful deletion of a collection.
    Contains the collection's unique identifier that confirms the
    deletion was applied to the specific collection record.
    """
    collection_id: int
