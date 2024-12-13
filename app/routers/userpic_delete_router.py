from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from app.database import get_session
from app.cache import get_cache
from app.decorators.locked_decorator import locked
from app.models.user_model import User, UserRole
from app.schemas.user_schemas import UserpicDeleteResponse
from app.errors import E
from app.hooks import Hook
from app.auth import auth
from app.repository import Repository
from app.managers.file_manager import FileManager
from app.constants import (
    LOC_PATH, ERR_RESOURCE_NOT_FOUND, ERR_RESOURCE_FORBIDDEN,
    HOOK_BEFORE_USERPIC_DELETE, HOOK_AFTER_USERPIC_DELETE)

router = APIRouter()


@router.delete("/user/{user_id}/userpic", summary="Remove a userpic.",
               response_class=JSONResponse, status_code=status.HTTP_200_OK,
               response_model=UserpicDeleteResponse, tags=["Users"])
@locked
async def userpic_delete(
    user_id: int,
    session=Depends(get_session), cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.reader))
) -> UserpicDeleteResponse:
    """
    Remove a userpic. Deletes the userpic if it exists and updates the
    user's data to remove the userpic. Allowed for the current user only.
    Requires the user to have a reader role or higher. Returns a 200
    response with the user ID. Raises a 403 error if the user attempts
    to delete a userpic for a different user or if the user's token is
    invalid, a 404 error if the user is not found, a 423 error if the
    application is locked.

    **Returns:**
    - `UserpicDeleteResponse`: A response schema containing the ID of
      the user from whom the userpic was deleted.

    **Raises:**
    - `403 Forbidden`: Raised if the current user attempts to delete the
      userpic of another user, or if the user does not have the required
      role or if the user's token is invalid.
    - `404 Not Found`: Raised if the user with the provided ID is not
      found.
    - `423 Locked`: Raised if the application is locked.

    **Hooks:**
    - `HOOK_BEFORE_USERPIC_DELETE`: Executes before the userpic is
      deleted.
    - `HOOK_AFTER_USERPIC_DELETE`: Executes after the userpic has been
      deleted.

    **Auth:**
    - The user must provide a valid `JWT token` in the request header.
    - The `reader`, `writer`, `editor`, or `admin` role is required to
      access this router.
    """
    user_repository = Repository(session, cache, User)
    user = await user_repository.select(id=user_id)

    if not user:
        raise E([LOC_PATH, "user_id"], user_id,
                ERR_RESOURCE_NOT_FOUND, status.HTTP_404_NOT_FOUND)

    elif user_id != current_user.id:
        raise E([LOC_PATH, "user_id"], user_id,
                ERR_RESOURCE_FORBIDDEN, status.HTTP_403_FORBIDDEN)

    hook = Hook(session, cache, current_user=current_user)
    await hook.do(HOOK_BEFORE_USERPIC_DELETE, current_user)

    if current_user.userpic_filename:
        await FileManager.delete(current_user.userpic_path)

    user_repository = Repository(session, cache, User)
    current_user.userpic_filename = None
    await user_repository.update(current_user, commit=False)

    await user_repository.commit()
    await hook.do(HOOK_AFTER_USERPIC_DELETE, current_user)

    return {"user_id": current_user.id}
