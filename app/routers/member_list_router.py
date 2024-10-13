from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from app.database import get_session
from app.cache import get_cache
from app.decorators.locked_decorator import locked
from app.models.user_model import User, UserRole
from app.models.member_model import Member
from app.schemas.member_schemas import (
    MemberListRequest, MemberListResponse)
from app.repository import Repository
from app.hooks import Hook
from app.auth import auth
from app.constants import HOOK_AFTER_MEMBER_LIST

router = APIRouter()


@router.get("/members", summary="Retrieve member list",
            response_class=JSONResponse, status_code=status.HTTP_200_OK,
            response_model=MemberListResponse, tags=["Members"])
@locked
async def member_list(
    schema=Depends(MemberListRequest),
    session=Depends(get_session), cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.reader))
) -> MemberListResponse:
    member_repository = Repository(session, cache, Member)

    members = await member_repository.select_all(**schema.__dict__)
    members_count = await member_repository.count_all(
        **schema.__dict__)

    hook = Hook(session, cache, current_user=current_user)
    await hook.do(HOOK_AFTER_MEMBER_LIST, members)

    return {
        "members": [member.to_dict() for member in members],
        "members_count": members_count,
    }
