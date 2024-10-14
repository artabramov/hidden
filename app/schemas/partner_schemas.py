from typing import Optional, Literal, List, Union
from pydantic import BaseModel, Field, field_validator
from app.schemas.user_schemas import UserSelectResponse
from app.validators.partner_validators import (
    validate_partner_name, validate_partner_summary, validate_partner_contacts)


class PartnerInsertRequest(BaseModel):
    partner_name: str = Field(..., min_length=1, max_length=256)
    partner_summary: Optional[str] = Field(max_length=512, default=None)
    partner_contacts: Optional[str] = Field(max_length=512, default=None)

    @field_validator("partner_name", mode="before")
    def validate_partner_name(cls, partner_name: str) -> str:
        return validate_partner_name(partner_name)

    @field_validator("partner_summary", mode="before")
    def validate_partner_summary(cls, partner_summary: str = None) -> Union[str, None]:  # noqa E501
        return validate_partner_summary(partner_summary)

    @field_validator("partner_contacts", mode="before")
    def validate_partner_contacts(cls, partner_summary: str = None) -> Union[str, None]:  # noqa E501
        return validate_partner_contacts(partner_summary)


class PartnerInsertResponse(BaseModel):
    partner_id: int


class PartnerSelectResponse(BaseModel):
    id: int
    created_date: int
    updated_date: int
    user_id: int
    partner_name: str
    partner_summary: Optional[str] = None
    partner_contacts: Optional[str] = None
    emblem_url: Optional[str] = None
    partner_user: UserSelectResponse


class PartnerUpdateRequest(BaseModel):
    partner_name: str = Field(..., min_length=1, max_length=256)
    partner_summary: Optional[str] = Field(max_length=512, default=None)
    partner_contacts: Optional[str] = Field(max_length=512, default=None)

    @field_validator("partner_name", mode="before")
    def validate_partner_name(cls, partner_name: str) -> str:
        return validate_partner_name(partner_name)

    @field_validator("partner_summary", mode="before")
    def validate_partner_summary(cls, partner_summary: str = None) -> Union[str, None]:  # noqa E501
        return validate_partner_summary(partner_summary)

    @field_validator("partner_contacts", mode="before")
    def validate_partner_contacts(cls, partner_summary: str = None) -> Union[str, None]:  # noqa E501
        return validate_partner_contacts(partner_summary)


class PartnerUpdateResponse(BaseModel):
    partner_id: int


class PartnerDeleteResponse(BaseModel):
    partner_id: int


class PartnerListRequest(BaseModel):
    partner_name__ilike: Optional[str] = None
    offset: int = Field(ge=0)
    limit: int = Field(ge=1, le=200)
    order_by: Literal["id", "created_date", "updated_date", "user_id",
                      "partner_name"]
    order: Literal["asc", "desc", "rand"]


class PartnerListResponse(BaseModel):
    partners: List[PartnerSelectResponse]
    partners_count: int


class EmblemUploadResponse(BaseModel):
    partner_id: int


class EmblemDeleteResponse(BaseModel):
    partner_id: int
