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


@router.put("/partner/{partner_id}", summary="Update a partner.",
            response_class=JSONResponse, status_code=status.HTTP_200_OK,
            response_model=PartnerUpdateResponse, tags=["Partners"])
@locked
async def partner_update(
    partner_id: int, schema: PartnerUpdateRequest,
    session=Depends(get_session), cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.editor))
) -> PartnerUpdateResponse:
    """
    Update a partner. The router retrieves the partner from the
    repository using the provided ID, ensures that the partner exists,
    and checks that the new partner name is unique. It updates the
    partner's attributes, executes related hooks, and returns the
    updated partner ID in a JSON response. The current user must have
    an editor role or higher. Returns a 200 response on success, a 404
    error if the partner is not found, a 422 error if validation
    failed or the partner name is duplicated, a 403 error if
    authentication failed or the user does not have the required
    permissions, and a 423 error if the application is locked.

    **Args:**
    - `partner_id`: The ID of the partner to update.
    - `PartnerUpdateRequest`: The request schema containing the updated
    partner data.

    **Returns:**
    - `PartnerUpdateResponse`: The response schema containing the ID of
    the updated partner.

    **Raises:**
    - `403 Forbidden`: Raised if the current user is not authenticated
    or does not have the required permissions.
    - `404 Not Found`: Raised if the partner with the specified ID
    does not exist.
    - `422 Unprocessable Entity`: Raised if arguments validation failed.
    - `423 Locked`: Raised if the application is locked.

    **Hooks:**
    - `HOOK_BEFORE_PARTNER_UPDATE`: Executes before the partner is
    updated.
    - `HOOK_AFTER_PARTNER_UPDATE`: Executes after the partner is updated.

    **Auth:**
    - The user must provide a valid `JWT token` in the request header.
    - `editor` or `admin` user role is required to access this router.
    """
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
    partner.partner_type = schema.partner_type
    partner.partner_region = schema.partner_region
    partner.partner_website = schema.partner_website
    partner.partner_contacts = schema.partner_contacts
    partner.partner_summary = schema.partner_summary
    await partner_repository.update(partner, commit=False)

    hook = Hook(session, cache, current_user=current_user)
    await hook.do(HOOK_BEFORE_PARTNER_UPDATE, partner)

    await partner_repository.commit()
    await hook.do(HOOK_AFTER_PARTNER_UPDATE, partner)

    return {"partner_id": partner.id}
