from fastapi import APIRouter, Depends, status, Request
from fastapi.responses import JSONResponse
from app.postgres import get_session
from app.redis import get_cache
from app.models.user_model import User, UserRole
from app.schemas.user_delete_schema import UserDeleteResponse
from app.repository import Repository
from app.error import E, LOC_PATH, ERR_VALUE_NOT_FOUND, ERR_VALUE_ERROR
from app.hook import Hook, HOOK_AFTER_USER_DELETE
from app.auth import auth

router = APIRouter()


@router.delete("/user/{user_id}", summary="Delete a user.",
               response_class=JSONResponse, status_code=status.HTTP_200_OK,
               response_model=UserDeleteResponse, tags=["Users"])
async def user_delete(
    user_id: int, request: Request,
    session=Depends(get_session), cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.admin)),
) -> UserDeleteResponse:
    """
    Deletes a user. The operation is restricted to admins and cannot be
    performed on the currently authenticated user. The user to delete
    should not have any relationships with other app objects.

    **Auth:**
    - The token must be included in the request header and contain auth
    data for an active user with the `admin` role.

    **Returns:**
    - `UserDeleteResponse`: Contains the ID of the deleted user.

    **Responses:**
    - `200 OK`: If the user is successfully deleted.
    - `401 Unauthorized`: If the token is invalid or lacks permissions.
    - `403 Forbidden`: If the token or secret key is missing.
    - `404 Not Found`: If the user is not found.
    - `422 Unprocessable Entity`: If deletion fails.
    - `423 Locked`: If the app is locked.

    **Hooks:**
    - `HOOK_AFTER_USER_DELETE`: Executes after the user is successfully
    deleted.
    """
    if user_id == current_user.id:
        raise E([LOC_PATH, "user_id"], user_id,
                ERR_VALUE_ERROR, status.HTTP_422_UNPROCESSABLE_ENTITY)

    user_repository = Repository(session, cache, User)
    user = await user_repository.select(id=user_id)

    if not user:
        raise E([LOC_PATH, "user_id"], user_id,
                ERR_VALUE_NOT_FOUND, status.HTTP_404_NOT_FOUND)

    try:
        await user_repository.delete(user)
    except Exception:
        raise E([LOC_PATH, "user_id"], user_id,
                ERR_VALUE_ERROR, status.HTTP_422_UNPROCESSABLE_ENTITY)

    hook = Hook(request.app, session, cache, current_user=current_user)
    await hook.call(HOOK_AFTER_USER_DELETE, user)

    return {"user_id": user.id}
