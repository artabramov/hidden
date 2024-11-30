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


@router.delete("/user/{user_id}/userpic", summary="Remove userpic",
               response_class=JSONResponse, status_code=status.HTTP_200_OK,
               response_model=UserpicDeleteResponse, tags=["Users"])
@locked
async def userpic_delete(
    user_id: int,
    session=Depends(get_session), cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.reader))
) -> UserpicDeleteResponse:
    """
    FastAPI router for deleting a userpic. Deletes the userpic if it
    exists and updates the user's data to remove the userpic. Allowed
    for the current user only. Requires the user to have a reader role
    or higher. Returns a 200 response with the user ID. Raises a 403
    error if the user attempts to delete a userpic for a different user
    or if the user's token is invalid.
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
