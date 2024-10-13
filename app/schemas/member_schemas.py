from typing import Optional, Literal, List, Union
from pydantic import BaseModel, Field, field_validator
from app.schemas.user_schemas import UserSelectResponse
from app.validators.member_validators import (
    validate_member_name, validate_member_summary, validate_member_contacts)


class MemberInsertRequest(BaseModel):
    member_name: str = Field(..., min_length=1, max_length=256)
    member_summary: Optional[str] = Field(max_length=512, default=None)
    member_contacts: Optional[str] = Field(max_length=512, default=None)

    @field_validator("member_name", mode="before")
    def validate_member_name(cls, member_name: str) -> str:
        return validate_member_name(member_name)

    @field_validator("member_summary", mode="before")
    def validate_member_summary(cls, member_summary: str = None) -> Union[str, None]:  # noqa E501
        return validate_member_summary(member_summary)

    @field_validator("member_contacts", mode="before")
    def validate_member_contacts(cls, member_summary: str = None) -> Union[str, None]:  # noqa E501
        return validate_member_contacts(member_summary)


class MemberInsertResponse(BaseModel):
    member_id: int


class MemberSelectResponse(BaseModel):
    id: int
    created_date: int
    updated_date: int
    user_id: int
    member_name: str
    member_summary: Optional[str] = None
    member_contacts: Optional[str] = None
    image_url: Optional[str] = None
    member_user: UserSelectResponse


class MemberUpdateRequest(BaseModel):
    member_name: str = Field(..., min_length=1, max_length=256)
    member_summary: Optional[str] = Field(max_length=512, default=None)
    member_contacts: Optional[str] = Field(max_length=512, default=None)

    @field_validator("member_name", mode="before")
    def validate_member_name(cls, member_name: str) -> str:
        return validate_member_name(member_name)

    @field_validator("member_summary", mode="before")
    def validate_member_summary(cls, member_summary: str = None) -> Union[str, None]:  # noqa E501
        return validate_member_summary(member_summary)

    @field_validator("member_contacts", mode="before")
    def validate_member_contacts(cls, member_summary: str = None) -> Union[str, None]:  # noqa E501
        return validate_member_contacts(member_summary)


class MemberUpdateResponse(BaseModel):
    member_id: int


class MemberDeleteResponse(BaseModel):
    member_id: int


class MemberListRequest(BaseModel):
    member_name__ilike: Optional[str] = None
    offset: int = Field(ge=0)
    limit: int = Field(ge=1, le=200)
    order_by: Literal["id", "created_date", "updated_date", "user_id",
                      "member_name"]
    order: Literal["asc", "desc", "rand"]


class MemberListResponse(BaseModel):
    members: List[MemberSelectResponse]
    members_count: int
