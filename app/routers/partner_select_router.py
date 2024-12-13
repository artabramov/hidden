from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from app.database import get_session
from app.cache import get_cache
from app.decorators.locked_decorator import locked
from app.models.user_model import User, UserRole
from app.models.partner_model import Partner
from app.schemas.partner_schemas import PartnerSelectResponse
from app.repository import Repository
from app.errors import E
from app.hooks import Hook
from app.auth import auth
from app.constants import (
    LOC_PATH, ERR_RESOURCE_NOT_FOUND, HOOK_AFTER_PARTNER_SELECT)

router = APIRouter()


@router.get("/partner/{partner_id}", summary="Retrieve partner.",
            response_class=JSONResponse, status_code=status.HTTP_200_OK,
            response_model=PartnerSelectResponse, tags=["Partners"])
@locked
async def partner_select(
    partner_id: int,
    session=Depends(get_session), cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.reader)),
) -> PartnerSelectResponse:
    """
    Retrieve a partner. The router fetches the partner from the
    repository using the provided ID, executes related hooks, and 
    returns the partner details in a JSON response. The current user
    should have a reader role or higher. Returns a 200 response on
    success, a 404 error if the partner is not found, a 403 error if
    authentication failed or the user does not have the required
    permissions, and a 423 error if the application is locked.

    **Args:**
    - `partner_id`: The ID of the partner to retrieve.

    **Returns:**
    - `PartnerSelectResponse`: The response schema containing the
      details of the selected partner.

    **Raises:**
    - `403 Forbidden`: Raised if the current user is not authenticated
      or does not have the required permissions.
    - `404 Not Found`: Raised if the partner with the specified ID does
      not exist.
    - `423 Locked`: Raised if the application is locked.

    **Hooks:**
    - `HOOK_AFTER_PARTNER_SELECT`: Executes after the partner is
      successfully selected.

    **Auth:**
    - The user must provide a valid `JWT token` in the request header.
    - `reader`, `writer`, `editor` or `admin` user role is required to
      access this router.
    """
    partner_repository = Repository(session, cache, Partner)
    partner = await partner_repository.select(id=partner_id)

    if not partner:
        raise E([LOC_PATH, "partner_id"], partner_id,
                ERR_RESOURCE_NOT_FOUND, status.HTTP_404_NOT_FOUND)

    hook = Hook(session, cache, current_user=current_user)
    await hook.do(HOOK_AFTER_PARTNER_SELECT, partner)

    return await partner.to_dict()
