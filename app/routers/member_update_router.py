from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from app.database import get_session
from app.cache import get_cache
from app.decorators.locked_decorator import locked
from app.models.user_model import User, UserRole
from app.models.member_model import Member
from app.schemas.member_schemas import (
    MemberUpdateRequest, MemberUpdateResponse)
from app.repository import Repository
from app.errors import E
from app.hooks import Hook
from app.auth import auth
from app.constants import (
    LOC_PATH, LOC_BODY, ERR_RESOURCE_NOT_FOUND, ERR_VALUE_DUPLICATED,
    HOOK_BEFORE_MEMBER_UPDATE, HOOK_AFTER_MEMBER_UPDATE)

router = APIRouter()


@router.put("/member/{member_id}", summary="Update a member",
            response_class=JSONResponse, status_code=status.HTTP_200_OK,
            response_model=MemberUpdateResponse, tags=["Members"])
@locked
async def member_update(
    member_id: int, schema: MemberUpdateRequest,
    session=Depends(get_session), cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.editor))
) -> MemberUpdateResponse:
    member_repository = Repository(session, cache, Member)

    member = await member_repository.select(id=member_id)
    if not member:
        raise E([LOC_PATH, "member_id"], member_id,
                ERR_RESOURCE_NOT_FOUND, status.HTTP_404_NOT_FOUND)

    member_exists = await member_repository.exists(
        member_name__eq=schema.member_name, id__ne=member.id)
    if member_exists:
        raise E([LOC_BODY, "member_name"], schema.member_name,
                ERR_VALUE_DUPLICATED, status.HTTP_422_UNPROCESSABLE_ENTITY)

    member.member_name = schema.member_name
    member.member_summary = schema.member_summary
    member.member_contacts = schema.member_contacts
    await member_repository.update(member, commit=False)

    hook = Hook(session, cache, current_user=current_user)
    await hook.do(HOOK_BEFORE_MEMBER_UPDATE, member)

    await member_repository.commit()
    await hook.do(HOOK_AFTER_MEMBER_UPDATE, member)

    return {"member_id": member.id}
