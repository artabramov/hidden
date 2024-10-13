from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from app.database import get_session
from app.cache import get_cache
from app.decorators.locked_decorator import locked
from app.models.user_model import User, UserRole
from app.models.member_model import Member
from app.schemas.member_schemas import MemberSelectResponse
from app.repository import Repository
from app.errors import E
from app.hooks import Hook
from app.auth import auth
from app.constants import (
    LOC_PATH, ERR_RESOURCE_NOT_FOUND, HOOK_AFTER_MEMBER_SELECT)

router = APIRouter()


@router.get("/member/{member_id}", summary="Retrieve member",
            response_class=JSONResponse, status_code=status.HTTP_200_OK,
            response_model=MemberSelectResponse, tags=["Members"])
@locked
async def member_select(
    member_id: int,
    session=Depends(get_session), cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.reader)),
) -> MemberSelectResponse:
    member_repository = Repository(session, cache, Member)
    member = await member_repository.select(id=member_id)

    if not member:
        raise E([LOC_PATH, "member_id"], member_id,
                ERR_RESOURCE_NOT_FOUND, status.HTTP_404_NOT_FOUND)

    hook = Hook(session, cache, current_user=current_user)
    await hook.do(HOOK_AFTER_MEMBER_SELECT, member)

    return member.to_dict()
