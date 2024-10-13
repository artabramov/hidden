"""
The module defines Pydantic schemas for managing favorites. Includes
schemas for inserting, selecting, deleting, and listing downloads.
"""

from typing import Literal, List
from pydantic import BaseModel, Field
from app.config import get_config
from app.schemas.document_schemas import DocumentSelectResponse

cfg = get_config()


class FavoriteInsertRequest(BaseModel):
    """
    Pydantic schema for request to create a new favorite entity.
    Requires the document ID to be specified.
    """
    document_id: int


class FavoriteInsertResponse(BaseModel):
    """
    Pydantic schema for the response after creating a new favorite
    entity. Includes the ID assigned to the newly created favorite.
    """
    favorite_id: int


class FavoriteSelectResponse(BaseModel):
    """
    Pydantic schema for the response after retrieving a favorite entity.
    Includes the favorite ID, date of creation, user ID, document ID,
    and the details of the related document.
    """
    id: int
    created_date: int
    user_id: int
    document_id: int
    favorite_document: DocumentSelectResponse


class FavoriteDeleteResponse(BaseModel):
    """
    Pydantic schema for the response after deleting a favorite entity.
    Includes the ID assigned to the deleted favorite.
    """
    favorite_id: int


class FavoriteListRequest(BaseModel):
    """
    Pydantic schema for requesting a list of favorite entities. Requires
    pagination options with offset and limit, and ordering criteria.
    """
    offset: int = Field(ge=0)
    limit: int = Field(ge=1, le=200)
    order_by: Literal["id", "created_date"]
    order: Literal["asc", "desc", "rand"]


class FavoriteListResponse(BaseModel):
    """
    Pydantic schema for the response when listing favorite entities.
    Includes a list of favorite entities and the total count of
    favorites that match the request criteria.
    """
    favorites: List[FavoriteSelectResponse]
    favorites_count: int
