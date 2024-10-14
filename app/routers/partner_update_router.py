from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from app.database import get_session
from app.cache import get_cache
from app.decorators.locked_decorator import locked
from app.models.user_model import User, UserRole
from app.models.partner_model import Partner
from app.schemas.partner_schemas import (
    PartnerUpdateRequest, PartnerUpdateResponse)
from app.repository import Repository
from app.errors import E
from app.hooks import Hook
from app.auth import auth
from app.constants import (
    LOC_PATH, LOC_BODY, ERR_RESOURCE_NOT_FOUND, ERR_VALUE_DUPLICATED,
    HOOK_BEFORE_PARTNER_UPDATE, HOOK_AFTER_PARTNER_UPDATE)

router = APIRouter()


@router.put("/partner/{partner_id}", summary="Update a partner",
            response_class=JSONResponse, status_code=status.HTTP_200_OK,
            response_model=PartnerUpdateResponse, tags=["Partners"])
@locked
async def partner_update(
    partner_id: int, schema: PartnerUpdateRequest,
    session=Depends(get_session), cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.editor))
) -> PartnerUpdateResponse:
    partner_repository = Repository(session, cache, Partner)

    partner = await partner_repository.select(id=partner_id)
    if not partner:
        raise E([LOC_PATH, "partner_id"], partner_id,
                ERR_RESOURCE_NOT_FOUND, status.HTTP_404_NOT_FOUND)

    partner_exists = await partner_repository.exists(
        partner_name__eq=schema.partner_name, id__ne=partner.id)
    if partner_exists:
        raise E([LOC_BODY, "partner_name"], schema.partner_name,
                ERR_VALUE_DUPLICATED, status.HTTP_422_UNPROCESSABLE_ENTITY)

    partner.partner_name = schema.partner_name
    partner.partner_summary = schema.partner_summary
    partner.partner_contacts = schema.partner_contacts
    await partner_repository.update(partner, commit=False)

    hook = Hook(session, cache, current_user=current_user)
    await hook.do(HOOK_BEFORE_PARTNER_UPDATE, partner)

    await partner_repository.commit()
    await hook.do(HOOK_AFTER_PARTNER_UPDATE, partner)

    return {"partner_id": partner.id}
