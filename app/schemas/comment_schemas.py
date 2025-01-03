"""
The module defines Pydantic schemas for managing comments. It includes
schemas for inserting, selecting, updating, deleting, and listing
comments.
"""

from typing import Literal, List, Optional
from pydantic import BaseModel, Field, field_validator
from app.filters.comment_filters import filter_comment_content


class CommentInsertRequest(BaseModel):
    """
    Pydantic schema for request to create a new comment entity. Requires
    the document ID and comment content to be specified.
    """
    document_id: int
    comment_content: str = Field(..., min_length=1, max_length=512)

    @field_validator("comment_content", mode="before")
    def filter_comment_content(cls, comment_content: str) -> str:
        return filter_comment_content(comment_content)


class CommentInsertResponse(BaseModel):
    """
    Pydantic schema for the response after creating a new comment
    entity. Includes the ID assigned to the newly created entity.
    """
    comment_id: int


class CommentSelectResponse(BaseModel):
    """
    Pydantic schema for the response after retrieving a comment entity.
    Includes the comment ID, creation and update dates, user ID,
    document ID, comment content, and details of the related user.
    """
    id: int
    created_date: int
    updated_date: int
    user_id: int
    user_name: str
    document_id: int
    comment_content: str


class CommentUpdateRequest(BaseModel):
    """
    Pydantic schema for request to update a comment entity. Requires
    the comment ID and comment content to be specified.
    """
    comment_content: str = Field(..., min_length=1, max_length=512)

    @field_validator("comment_content", mode="before")
    def filter_comment_content(cls, comment_content: str) -> str:
        return filter_comment_content(comment_content)


class CommentUpdateResponse(BaseModel):
    """
    Pydantic schema for the response after updating a comment entity.
    Includes the ID assigned to the updated comment.
    """
    comment_id: int


class CommentDeleteResponse(BaseModel):
    """
    Pydantic schema for the response after deleting a comment entity.
    Includes the ID assigned to the deleted comment.
    """
    comment_id: int


class CommentListRequest(BaseModel):
    """
    Pydantic schema for requesting a list of comment entities. Requires
    document ID, pagination options with offset and limit, and ordering
    criteria.
    """
    document_id__eq: Optional[int] = None
    offset: int = Field(ge=0)
    limit: int = Field(ge=1, le=200)
    order_by: Literal["id", "created_date"]
    order: Literal["asc", "desc"]


class CommentListResponse(BaseModel):
    """
    Pydantic schema for the response when listing comment entities.
    Includes a list of comment entities and the total count of comments
    that match the request criteria.
    """
    comments: List[CommentSelectResponse]
    comments_count: int
