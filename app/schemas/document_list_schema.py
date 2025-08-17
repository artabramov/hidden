"""
The module defines Pydantic schemas for listing documents.
"""

from typing import Optional, Literal, List, Union
from pydantic import BaseModel, Field, field_validator
from app.schemas.document_select_schema import DocumentSelectResponse
from app.validators.tag_value_validator import tag_value_validate
from app.config import get_config

cfg = get_config()


class DocumentListRequest(BaseModel):
    """
    Request schema for listing documents with pagination and filtering
    options. Includes an optional filter by user, collection, pagination
    parameters like offset and limit, the field to order the results by,
    and the direction of ordering. The order direction can be ascending,
    descending, or random.
    """
    user_id__eq: Optional[int] = None
    collection_id__eq: Optional[int] = None
    tag_value__eq: Optional[str] = None
    offset: Optional[int] = Field(ge=0, default=None)
    limit: Optional[int] = Field(ge=1, default=None)
    order_by: Optional[Literal[
        "id", "user_id", "collection_id", "original_filename_index",
        "document_filesize_index", "document_mimetype_index"]] = None
    order: Optional[Literal["asc", "desc", "rand"]] = None

    class Config:
        """Strips whitespaces at the beginning and end of all values."""
        str_strip_whitespace = True

    @field_validator("tag_value__eq", mode="before")
    def validate_tag_value(cls, tag_value: list = None) -> Union[list, None]:
        """Validates document tags."""
        return tag_value_validate(tag_value)


class DocumentListResponse(BaseModel):
    """
    Response schema for listing documents. Contains a list of documents
    and the total count of documents available.
    """
    documents: List[DocumentSelectResponse]
    documents_count: int
