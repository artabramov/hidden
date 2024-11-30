from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from app.database import get_session
from app.cache import get_cache
from app.decorators.locked_decorator import locked
from app.models.user_model import User, UserRole
from app.models.partner_model import Partner
from app.schemas.partner_schemas import PartnerpicDeleteResponse
from app.errors import E
from app.hooks import Hook
from app.auth import auth
from app.repository import Repository
from app.managers.file_manager import FileManager
from app.constants import (
    LOC_PATH, ERR_RESOURCE_NOT_FOUND, HOOK_BEFORE_PARTNERPIC_DELETE,
    HOOK_AFTER_PARTNERPIC_DELETE)

router = APIRouter()


@router.delete("/partner/{partner_id}/partnerpic", summary="Remove partnerpic",
               response_class=JSONResponse, status_code=status.HTTP_200_OK,
               response_model=PartnerpicDeleteResponse, tags=["Partners"])
@locked
async def partnerpic_delete(
    partner_id: int,
    session=Depends(get_session), cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.editor))
) -> PartnerpicDeleteResponse:
    partner_repository = Repository(session, cache, Partner)
    partner = await partner_repository.select(id=partner_id)

    if not partner:
        raise E([LOC_PATH, "partner_id"], partner_id,
                ERR_RESOURCE_NOT_FOUND, status.HTTP_404_NOT_FOUND)

    hook = Hook(session, cache, current_user=current_user)
    await hook.do(HOOK_BEFORE_PARTNERPIC_DELETE, partner)

    if partner.partnerpic_filename:
        await FileManager.delete(partner.partnerpic_path)

    partner.partnerpic_filename = None
    await partner_repository.update(partner, commit=False)

    await partner_repository.commit()
    await hook.do(HOOK_AFTER_PARTNERPIC_DELETE, partner)

    return {"partner_id": partner.id}
