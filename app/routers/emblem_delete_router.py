from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from app.database import get_session
from app.cache import get_cache
from app.decorators.locked_decorator import locked
from app.models.user_model import User, UserRole
from app.models.member_model import Member
from app.schemas.member_schemas import EmblemDeleteResponse
from app.errors import E
from app.hooks import Hook
from app.auth import auth
from app.repository import Repository
from app.managers.file_manager import FileManager
from app.constants import (
    LOC_PATH, ERR_RESOURCE_NOT_FOUND, HOOK_BEFORE_EMBLEM_DELETE,
    HOOK_AFTER_EMBLEM_DELETE)

router = APIRouter()


@router.delete("/member/{member_id}/emblem", summary="Remove member emblem",
               response_class=JSONResponse, status_code=status.HTTP_200_OK,
               response_model=EmblemDeleteResponse, tags=["Members"])
@locked
async def emblem_delete(
    member_id: int,
    session=Depends(get_session), cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.editor))
) -> EmblemDeleteResponse:
    member_repository = Repository(session, cache, Member)
    member = await member_repository.select(id=member_id)

    if not member:
        raise E([LOC_PATH, "member_id"], member_id,
                ERR_RESOURCE_NOT_FOUND, status.HTTP_404_NOT_FOUND)

    hook = Hook(session, cache, current_user=current_user)
    await hook.do(HOOK_BEFORE_EMBLEM_DELETE, member)

    if member.emblem_filename:
        await FileManager.delete(member.emblem_path)

    member.emblem_filename = None
    await member_repository.update(member, commit=False)

    await member_repository.commit()
    await hook.do(HOOK_AFTER_EMBLEM_DELETE, member)

    return {"member_id": member.id}
