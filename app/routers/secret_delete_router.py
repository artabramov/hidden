from fastapi import APIRouter, status, Depends, Request
from fastapi.responses import JSONResponse
from app.schemas.secret_delete_schema import SecretDeleteResponse
from app.hook import Hook, HOOK_AFTER_SECRET_DELETE
from app.auth import auth
from app.models.user_model import User, UserRole
from app.postgres import get_session
from app.redis import get_cache
from app.config import get_config
from app.managers.file_manager import FileManager

cfg = get_config()
router = APIRouter()


@router.delete("/secret", summary="Delete the secret key.",
               response_class=JSONResponse, status_code=status.HTTP_200_OK,
               response_model=SecretDeleteResponse,
               tags=["Secret"])
async def secret_delete(
    request: Request,
    session=Depends(get_session), cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.admin))
) -> SecretDeleteResponse:
    """
    Deletes the secret key. Removes the secret key file from the
    specified path.

    **Auth:**
    - The token must be included in the request header and contain auth
    data for an active user with the `admin` role.

    **Returns:**
    - `SecretDeleteResponse`: Contains the path of the deleted secret
    key.

    **Responses:**
    - `200 OK`: If the secret key is successfully deleted.
    - `401 Unauthorized`: If the token is invalid or lacks permissions.
    - `403 Forbidden`: If the token or secret key is missing.
    - `423 Locked`: If the app is locked.

    **Hooks:**
    - `HOOK_AFTER_SECRET_DELETE`: Executes after the secret key is
    successfully deleted.
    """
    await FileManager.delete(cfg.SECRET_KEY_PATH)

    hook = Hook(request.app, session, cache, current_user=current_user)
    await hook.call(HOOK_AFTER_SECRET_DELETE, cfg.SECRET_KEY_PATH)

    return {
        "secret_path": cfg.SECRET_KEY_PATH
    }
