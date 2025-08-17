from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from app.postgres import get_session
from app.redis import get_cache
from app.models.user_model import User, UserRole
from app.schemas.userpic_delete_schema import UserpicDeleteResponse
from app.error import E, LOC_PATH, ERR_VALUE_ERROR
from app.hook import Hook, HOOK_AFTER_USERPIC_DELETE
from app.auth import auth
from app.repository import Repository
from app.managers.file_manager import FileManager

router = APIRouter()


@router.delete("/user/{user_id}/userpic", summary="Delete a userpic.",
               response_class=JSONResponse, status_code=status.HTTP_200_OK,
               response_model=UserpicDeleteResponse, tags=["Users"])
async def userpic_delete(
    user_id: int,
    session=Depends(get_session), cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.reader))
) -> UserpicDeleteResponse:
    """
    Deletes a userpic. Removes the current user's profile picture and
    updates the user record accordingly.

    **Auth:**
    - The token must be included in the request header and contain auth
    data for an active user with the `reader`, `writer`, `editor`, or
    `admin` role.

    **Returns:**
    - `UserpicDeleteResponse`: Contains the ID of the user whose profile
    picture was deleted.

    **Responses:**
    - `200 OK`: If the profile picture is successfully deleted.
    - `401 Unauthorized`: If the token is invalid or lacks permissions.
    - `403 Forbidden`: If the token or secret key is missing.
    - `422 Unprocessable Entity`: If parameters validation fails.
    - `423 Locked`: If the app is locked.

    **Hooks:**
    - `HOOK_AFTER_USERPIC_DELETE`: Executes after the profile picture is
    successfully deleted.
    """
    if user_id != current_user.id:
        raise E([LOC_PATH, "user_id"], user_id,
                ERR_VALUE_ERROR, status.HTTP_422_UNPROCESSABLE_ENTITY)

    if current_user.has_userpic:
        await FileManager.delete(current_user.userpic_path)

        current_user.userpic_filename = None

        user_repository = Repository(session, cache, User)
        await user_repository.update(current_user)

    hook = Hook(session, cache, current_user=current_user)
    await hook.call(HOOK_AFTER_USERPIC_DELETE, current_user)

    return {"user_id": current_user.id}
