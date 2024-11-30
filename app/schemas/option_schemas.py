"""
The module defines Pydantic schemas for managing options.
Includes schemas for inserting or updating, selecting, deleting,
and listing options.
"""

from typing import Literal, List, Optional
from pydantic import BaseModel, Field, field_validator
from app.filters.option_filters import filter_option_key, filter_option_value


class OptionInsertRequest(BaseModel):
    """
    Pydantic schema for request to update an option entity. Requires
    the option key and option value to be specified.
    """
    option_key: str = Field(..., pattern=r"^[a-zA-Z_0-9]{2,40}$")
    option_value: str = Field(..., max_length=512)

    @field_validator("option_key", mode="before")
    def filter_option_key(cls, option_key: str) -> str:
        return filter_option_key(option_key)

    @field_validator("option_value", mode="before")
    def filter_option_value(cls, option_value: str) -> str:
        return filter_option_value(option_value)


class OptionInsertResponse(BaseModel):
    """
    Pydantic schema for the response after updating an option entity.
    Includes the key of the updated option.
    """
    option_key: str


class OptionSelectResponse(BaseModel):
    """
    Pydantic schema for the response after selecting an option entity.
    Includes the option ID, creation and update dates, option key, and
    option value.
    """
    id: int
    created_date: int
    updated_date: int
    option_key: str
    option_value: str


class OptionUpdateRequest(BaseModel):
    """
    Pydantic schema for the request to update an existing option entity.
    Requires the option value to be specified.
    """
    option_value: str = Field(..., max_length=512)

    @field_validator("option_value", mode="before")
    def filter_option_value(cls, option_value: str) -> str:
        return filter_option_value(option_value)


class OptionUpdateResponse(BaseModel):
    """
    Pydantic schema for the response after updating an option entity.
    Includes the key of the updated option.
    """
    option_key: str


class OptionDeleteResponse(BaseModel):
    """
    Pydantic schema for the response after deleting an option entity.
    Includes the key of the deleted option, if available.
    """
    option_key: Optional[str] = None


class OptionListRequest(BaseModel):
    """
    Pydantic schema for requesting a list of option entities. Requires
    pagination options with offset and limit, and ordering criteria.
    """
    offset: int = Field(ge=0)
    limit: int = Field(ge=1, le=200)
    order_by: Literal["id", "created_date", "updated_date", "option_key"]
    order: Literal["asc", "desc"]


class OptionListResponse(BaseModel):
    """
    Pydantic schema for the response when listing option entities.
    Includes a list of option entities and the total count of options
    that match the request criteria.
    """
    options: List[OptionSelectResponse]
    options_count: int
