from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from app.database import get_session
from app.cache import get_cache
from app.decorators.locked_decorator import locked
from app.models.user_model import User, UserRole
from app.models.partner_model import Partner
from app.schemas.partner_schemas import (
    PartnerInsertRequest, PartnerInsertResponse)
from app.repository import Repository
from app.errors import E
from app.hooks import Hook
from app.auth import auth
from app.constants import (
    LOC_BODY, ERR_VALUE_DUPLICATED, HOOK_BEFORE_PARTNER_INSERT,
    HOOK_AFTER_PARTNER_INSERT)

router = APIRouter()


@router.post("/partner", summary="Create a new partner",
             response_class=JSONResponse, status_code=status.HTTP_201_CREATED,
             response_model=PartnerInsertResponse, tags=["Partners"])
@locked
async def partner_insert(
    schema: PartnerInsertRequest,
    session=Depends(get_session), cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.writer))
) -> PartnerInsertResponse:
    partner_repository = Repository(session, cache, Partner)

    partner_exists = await partner_repository.exists(
        partner_name__eq=schema.partner_name)

    if partner_exists:
        raise E([LOC_BODY, "partner_name"], schema.partner_name,
                ERR_VALUE_DUPLICATED, status.HTTP_422_UNPROCESSABLE_ENTITY)

    partner = Partner(
        current_user.id, schema.partner_name,
        partner_summary=schema.partner_summary,
        partner_contacts=schema.partner_contacts)
    await partner_repository.insert(partner, commit=False)

    hook = Hook(session, cache, current_user=current_user)
    await hook.do(HOOK_BEFORE_PARTNER_INSERT, partner)

    await partner_repository.commit()
    await hook.do(HOOK_AFTER_PARTNER_INSERT, partner)

    return {"partner_id": partner.id}
