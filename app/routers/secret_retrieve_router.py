import os
from fastapi import APIRouter, status, Depends, Request
from fastapi.responses import JSONResponse
from app.schemas.secret_retrieve_schema import SecretRetrieveResponse
from app.hook import Hook, HOOK_AFTER_SECRET_RETRIEVE
from app.auth import auth
from app.models.user_model import User, UserRole
from app.postgres import get_session
from app.redis import get_cache
from app.config import get_config
from app.helpers.secret_helper import secret_read

cfg = get_config()
router = APIRouter()


@router.get("/secret", summary="Retrieve a secret key.",
            response_class=JSONResponse, status_code=status.HTTP_200_OK,
            response_model=SecretRetrieveResponse,
            tags=["Secret"])
async def secret_retrieve(
    request: Request,
    session=Depends(get_session), cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.admin))
) -> SecretRetrieveResponse:
    """
    Retrieves a secret key. Fetches the secret key from the stored path
    and returns the key along with its location.

    **Auth:**
    - The token must be included in the request header and contain auth
    data for an active user with the `admin` role.

    **Returns:**
    - `SecretRetrieveResponse`: Response on success.

    **Responses:**
    - `200 OK`: If the secret key is successfully retrieved.
    - `401 Unauthorized`: If the token is invalid or lacks permissions.
    - `403 Forbidden`: If the token or secret key is missing.
    - `423 Locked`: If the app is locked.

    **Hooks:**
    - `HOOK_AFTER_SECRET_RETRIEVE`: Executes after the secret key is
    successfully retrieved.
    """
    secret_key = await secret_read()
    secret_path = cfg.SECRET_KEY_PATH
    created_date = int(os.path.getctime(secret_path))

    hook = Hook(request.app, session, cache, current_user=current_user)
    await hook.call(HOOK_AFTER_SECRET_RETRIEVE, secret_key, secret_path,
                    created_date)

    return {
        "created_date": created_date,
        "secret_key": secret_key,
        "secret_path": secret_path,
    }
