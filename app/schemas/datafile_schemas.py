"""
The module defines Pydantic schemas for managing datafiles. Includes
schemas for inserting, selecting, updating, deleting, and listing
datafiles.
"""

from typing import Optional, Literal, List, Union
from pydantic import BaseModel, Field, field_validator
from app.schemas.user_schemas import UserSelectResponse
from app.schemas.revision_schemas import RevisionSelectResponse
from app.validators.datafile_validators import (
    validate_datafile_summary, validate_datafile_name, validate_tags)


class DatafileUploadResponse(BaseModel):
    datafile_id: int
    revision_id: int


class DatafileReplaceResponse(BaseModel):
    datafile_id: int
    revision_id: int


class DatafileSelectResponse(BaseModel):
    """
    Pydantic schema for the response after retrieving a datafile entity.
    Includes the datafile ID, creation and update dates, user ID,
    collection ID, datafile name, summary, size, and various counts
    such as revisions, comments, downloads, and favorites. Also includes
    the datafile tags and the latest revision details.
    """
    id: int
    created_date: int
    updated_date: int
    user_id: int
    collection_id: Optional[int]
    member_id: Optional[int]

    datafile_name: str
    datafile_summary: Optional[str] = None
    comments_count: int
    revisions_count: int
    revisions_size: int
    downloads_count: int

    datafile_tags: list
    datafile_user: UserSelectResponse
    latest_revision: RevisionSelectResponse


class DatafileUpdateRequest(BaseModel):
    """
    Pydantic schema for request to update an existing datafile entity.
    Requires the datafile ID and collection ID to be specified, and
    optionally the datafile name, summary, and tags.
    """
    collection_id: Optional[int] = None
    member_id: Optional[int] = None
    datafile_name: str = Field(..., min_length=1, max_length=256)
    datafile_summary: Optional[str] = Field(max_length=512, default=None)
    tags: Optional[str] = Field(max_length=256, default=None)

    @field_validator("datafile_summary", mode="before")
    def validate_datafile_summary(cls, datafile_summary: str = None) -> Union[str, None]:  # noqa E501
        return validate_datafile_summary(datafile_summary)

    @field_validator("datafile_name", mode="before")
    def validate_datafile_name(cls, datafile_name: str) -> str:
        return validate_datafile_name(datafile_name)

    @field_validator("tags", mode="before")
    def validate_tags(cls, tags: str = None) -> Union[str, None]:
        return validate_tags(tags)


class DatafileUpdateResponse(BaseModel):
    """
    Pydantic schema for the response after updating a datafile entity.
    Includes the ID assigned to the updated datafile.
    """
    datafile_id: int
    revision_id: int


class DatafileDeleteResponse(BaseModel):
    """
    Pydantic schema for the response after updating a datafile entity.
    Includes the ID assigned to the deleted datafile.
    """
    datafile_id: int


class DatafileListRequest(BaseModel):
    """
    Pydantic schema for requesting a list of datafile entities. Requires
    pagination options with offset and limit, ordering criteria, and
    optional filters for datafile name and tag value.
    """
    collection_id__eq: Optional[int] = None
    datafile_name__ilike: Optional[str] = None
    comments_count__ge: Optional[int] = None
    comments_count__le: Optional[int] = None
    revisions_count__ge: Optional[int] = None
    revisions_count__le: Optional[int] = None
    revisions_size__ge: Optional[int] = None
    revisions_size__le: Optional[int] = None
    downloads_count__ge: Optional[int] = None
    downloads_count__le: Optional[int] = None
    tag_value__eq: Optional[str] = None
    offset: int = Field(ge=0)
    limit: int = Field(ge=1, le=200)
    order_by: Literal["id", "created_date", "updated_date", "user_id",
                      "collection_id", "datafile_name", "comments_count",
                      "revisions_count", "revisions_size", "downloads_count"]
    order: Literal["asc", "desc", "rand"]


class DatafileListResponse(BaseModel):
    """
    Pydantic schema for the response when listing datafile entities.
    Includes a list of datafile entities and the total count of
    datafile that match the request criteria.
    """
    datafiles: List[DatafileSelectResponse]
    datafiles_count: int
