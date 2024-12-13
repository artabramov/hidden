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


@router.post("/partner", summary="Create a partner.",
             response_class=JSONResponse, status_code=status.HTTP_201_CREATED,
             response_model=PartnerInsertResponse, tags=["Partners"])
@locked
async def partner_insert(
    schema: PartnerInsertRequest,
    session=Depends(get_session), cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.writer))
) -> PartnerInsertResponse:
    """
    Create a partner. The router checks if a partner with the same name
    already exists in the repository. If it does, it raises a validation
    error. If the partner is unique, it creates the partner and executes
    relevant hooks before and after insertion, and returns the created
    partner ID in a JSON response. The current user should have a writer
    role or higher. Returns a 201 response on success, a 422 error if
    arguments validation failed or the partner name is duplicated, a 403
    error if authentication failed or the user does not have the
    required permissions, and a 423 error if the application is locked.

    **Args:**
    - `PartnerInsertRequest`: A request schema containing the details
      for the new partner.

    **Returns:**
    - `PartnerInsertResponse`: The response schema containing the ID of
      the newly created partner.

    **Raises:**
    - `403 Forbidden`: Raised if the current user is not authenticated
      or does not have the required permissions.
    - `422 Unprocessable Entity`: Raised if arguments validation failed
      or the partner name is already exist.
    - `423 Locked`: Raised if the application is locked.

    **Auth:**
    - The user must provide a valid `JWT token` in the request header.
    - `writer`, `editor` or `admin` role is required to access this
      router.
    """
    partner_repository = Repository(session, cache, Partner)

    partner_exists = await partner_repository.exists(
        partner_name__eq=schema.partner_name)

    if partner_exists:
        raise E([LOC_BODY, "partner_name"], schema.partner_name,
                ERR_VALUE_DUPLICATED, status.HTTP_422_UNPROCESSABLE_ENTITY)

    partner = Partner(
        current_user.id, schema.partner_name,
        partner_type=schema.partner_type,
        partner_region=schema.partner_region,
        partner_website=schema.partner_website,
        partner_contacts=schema.partner_contacts,
        partner_summary=schema.partner_summary)
    await partner_repository.insert(partner, commit=False)

    hook = Hook(session, cache, current_user=current_user)
    await hook.do(HOOK_BEFORE_PARTNER_INSERT, partner)

    await partner_repository.commit()
    await hook.do(HOOK_AFTER_PARTNER_INSERT, partner)

    return {"partner_id": partner.id}
