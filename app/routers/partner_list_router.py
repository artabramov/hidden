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


@router.get("/partners", summary="Retrieve a list of partners.",
            response_class=JSONResponse, status_code=status.HTTP_200_OK,
            response_model=PartnerListResponse, tags=["Partners"])
@locked
async def partner_list(
    schema=Depends(PartnerListRequest),
    session=Depends(get_session), cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.reader))
) -> PartnerListResponse:
    """
    Retrieve a list of partners. This endpoint fetches all partners from
    the repository based on the provided filter criteria and executes
    related hooks. The current user must have a reader role or higher.
    Returns a 200 response on success, a 403 error if authentication
    failed or the user does not have the required permissions, a 422
    error if arguments validation failed, and a 423 error if the
    application is locked.

    **Args:**
    - `PartnerListRequest`: The request schema containing filter and
      pagination details.

    **Returns:**
    - `PartnerListResponse`: The response schema containing the list
      of partners and the total count.

    **Raises:**
    - `403 Forbidden`: Raised if the current user is not authenticated
      or does not have the required `reader` role.
    - `422 Unprocessable Entity`:  Raised if arguments validation failed.
    - `423 Locked`: Raised if the application is locked.

    **Hooks:**
    - `HOOK_AFTER_PARTNER_LIST`: Executes after the partners are
      retrieved.

    **Auth:**
    - The user must provide a valid `JWT token` in the request header.
    - `reader`, `writer`, `editor`, `admin` user role is required to
      access this router.
    """
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
