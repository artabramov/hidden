from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from app.database import get_session
from app.cache import get_cache
from app.decorators.locked_decorator import locked
from app.models.user_model import User, UserRole
from app.models.member_model import Member
from app.schemas.member_schemas import (
    MemberInsertRequest, MemberInsertResponse)
from app.repository import Repository
from app.errors import E
from app.hooks import Hook
from app.auth import auth
from app.constants import (
    LOC_BODY, ERR_VALUE_DUPLICATED, HOOK_BEFORE_MEMBER_INSERT,
    HOOK_AFTER_MEMBER_INSERT)

router = APIRouter()


@router.post("/member", summary="Create a new member",
             response_class=JSONResponse, status_code=status.HTTP_201_CREATED,
             response_model=MemberInsertResponse, tags=["Members"])
@locked
async def member_insert(
    schema: MemberInsertRequest,
    session=Depends(get_session), cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.writer))
) -> MemberInsertResponse:
    member_repository = Repository(session, cache, Member)

    member_exists = await member_repository.exists(
        member_name__eq=schema.member_name)

    if member_exists:
        raise E([LOC_BODY, "member_name"], schema.member_name,
                ERR_VALUE_DUPLICATED, status.HTTP_422_UNPROCESSABLE_ENTITY)

    member = Member(
        current_user.id, schema.member_name,
        member_summary=schema.member_summary,
        member_contacts=schema.member_contacts)
    await member_repository.insert(member, commit=False)

    hook = Hook(session, cache, current_user=current_user)
    await hook.do(HOOK_BEFORE_MEMBER_INSERT, member)

    await member_repository.commit()
    await hook.do(HOOK_AFTER_MEMBER_INSERT, member)

    return {"member_id": member.id}
