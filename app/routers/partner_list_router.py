from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from app.database import get_session
from app.cache import get_cache
from app.decorators.locked_decorator import locked
from app.models.user_model import User, UserRole
from app.models.partner_model import Partner
from app.schemas.partner_schemas import (
    PartnerListRequest, PartnerListResponse)
from app.repository import Repository
from app.hooks import Hook
from app.auth import auth
from app.constants import HOOK_AFTER_PARTNER_LIST

router = APIRouter()


@router.get("/partners", summary="Retrieve partner list",
            response_class=JSONResponse, status_code=status.HTTP_200_OK,
            response_model=PartnerListResponse, tags=["Partners"])
@locked
async def partner_list(
    schema=Depends(PartnerListRequest),
    session=Depends(get_session), cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.reader))
) -> PartnerListResponse:
    partner_repository = Repository(session, cache, Partner)

    partners = await partner_repository.select_all(**schema.__dict__)
    partners_count = await partner_repository.count_all(
        **schema.__dict__)

    hook = Hook(session, cache, current_user=current_user)
    await hook.do(HOOK_AFTER_PARTNER_LIST, partners)

    return {
        "partners": [await partner.to_dict() for partner in partners],
        "partners_count": partners_count,
    }
