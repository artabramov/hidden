"""Pydantic schemas for collection deletion."""

from pydantic import BaseModel


class CollectionDeleteResponse(BaseModel):
    """
    Response schema for collection deletion. Contains the deleted
    collection ID.
    """

    collection_id: int
