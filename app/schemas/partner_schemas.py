"""
The module defines Pydantic schemas for managing partners. Includes
schemas for inserting, updating, selecting, deleting, and listing
partner entities.
"""

from typing import Optional, Literal, List, Union
from pydantic import BaseModel, Field, field_validator
from app.filters.partner_filters import (
    filter_partner_name, filter_partner_contacts, filter_partner_summary)


class PartnerInsertRequest(BaseModel):
    """
    Pydantic schema for the request to insert a new partner entity.
    Requires the partner name, and optionally partner contacts, and
    summary.
    """
    partner_name: str = Field(..., min_length=1, max_length=256)
    partner_contacts: Optional[str] = Field(max_length=512, default=None)
    partner_summary: Optional[str] = Field(max_length=512, default=None)

    @field_validator("partner_name", mode="before")
    def filter_partner_name(cls, partner_name: str) -> str:
        return filter_partner_name(partner_name)

    @field_validator("partner_contacts", mode="before")
    def filter_partner_contacts(cls, partner_contacts: str) -> Union[str, None]:  # noqa E501
        return filter_partner_contacts(partner_contacts)

    @field_validator("partner_summary", mode="before")
    def filter_partner_summary(cls, partner_summary: str = None) -> Union[str, None]:  # noqa E501
        return filter_partner_summary(partner_summary)


class PartnerInsertResponse(BaseModel):
    """
    Pydantic schema for the response after inserting a new partner
    entity. Includes the ID of the newly created partner.
    """
    partner_id: int


class PartnerSelectResponse(BaseModel):
    """
    Pydantic schema for the response after selecting a partner entity.
    Includes the partner ID, creation and update dates, partner name,
    contacts, summary, and picture URL.
    """
    id: int
    created_date: int
    updated_date: int
    user_id: int
    user_name: str
    partner_name: str
    partner_contacts: Optional[str] = None
    partner_summary: Optional[str] = None
    partnerpic_url: Optional[str] = None


class PartnerUpdateRequest(BaseModel):
    """
    Pydantic schema for the request to update an existing partner entity.
    Requires the updated partner name, and optionally the partner
    contacts, and summary.
    """
    partner_name: str = Field(..., min_length=1, max_length=256)
    partner_contacts: Optional[str] = Field(max_length=512, default=None)
    partner_summary: Optional[str] = Field(max_length=512, default=None)

    @field_validator("partner_name", mode="before")
    def filter_partner_name(cls, partner_name: str) -> str:
        return filter_partner_name(partner_name)

    @field_validator("partner_contacts", mode="before")
    def filter_partner_contacts(cls, partner_contacts: str) -> str:
        return filter_partner_contacts(partner_contacts)

    @field_validator("partner_summary", mode="before")
    def filter_partner_summary(cls, partner_summary: str = None) -> Union[str, None]:  # noqa E501
        return filter_partner_summary(partner_summary)


class PartnerUpdateResponse(BaseModel):
    """
    Pydantic schema for the response after updating a partner entity.
    Includes the ID of the updated partner.
    """
    partner_id: int


class PartnerDeleteResponse(BaseModel):
    """
    Pydantic schema for the response after deleting a partner entity.
    Includes the ID of the deleted partner.
    """
    partner_id: int


class PartnerListRequest(BaseModel):
    """
    Pydantic schema for requesting a list of partner entities. Requires
    pagination options with offset and limit, and ordering criteria.
    Optionally filters by partner name.
    """
    partner_name__ilike: Optional[str] = None
    offset: int = Field(ge=0)
    limit: int = Field(ge=1, le=200)
    order_by: Literal[
        "id", "created_date", "updated_date", "user_id", "partner_name"]
    order: Literal["asc", "desc", "rand"]


class PartnerListResponse(BaseModel):
    """
    Pydantic schema for the response when listing partner entities.
    Includes a list of partner entities and the total count of partners
    that match the request criteria.
    """
    partners: List[PartnerSelectResponse]
    partners_count: int


class PartnerpicUploadResponse(BaseModel):
    """
    Pydantic schema for the response after uploading an image for
    a partner. Includes the partner ID.
    """
    partner_id: int


class PartnerpicDeleteResponse(BaseModel):
    """
    Pydantic schema for the response after deleting an image for
    a partner. Includes the partner ID.
    """
    partner_id: int
