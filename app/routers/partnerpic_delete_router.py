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


@router.delete("/partner/{partner_id}/partnerpic",
               summary="Delete a partner image.",
               response_class=JSONResponse, status_code=status.HTTP_200_OK,
               response_model=PartnerpicDeleteResponse, tags=["Partners"])
@locked
async def partnerpic_delete(
    partner_id: int,
    session=Depends(get_session), cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.editor))
) -> PartnerpicDeleteResponse:
    """
    Delete a partner image. This router deletes the image associated
    with a given partner ID if it exists. It also triggers hooks before
    and after the deletion process, and returns the partner ID in a JSON
    response. The current user must have an editor role or higher.
    Returns a 200 response on success, a 404 error if the partner is
    not found, a 403 error if authentication failed or the user does
    not have the required permissions, and a 423 error if the
    application is locked.

    **Args:**
    - `partner_id`: The ID of the partner whose image is to be deleted.

    **Returns:**
    - `PartnerpicDeleteResponse`: Response containing the partner ID
      after the image is successfully removed.

    **Raises:**
    - `403 Forbidden`: Raised if the current user is not authenticated
      or does not have the required permissions.
    - `404 Not Found`: Raised if the partner with the specified ID
      does not exist.
    - `423 Locked`: Raised if the application is locked.

    **Hooks:**
    - `HOOK_BEFORE_PARTNERPIC_DELETE`: Executes before the image is
      deleted.
    - `HOOK_AFTER_PARTNERPIC_DELETE`: Executes after the image has been
      deleted.

    **Auth:**
    - The user must provide a valid JWT token in the request header.
    - The `editor` or `admin` role is required to access this endpoint.
    """
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
