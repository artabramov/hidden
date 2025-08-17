from fastapi import APIRouter, Depends, status, Request
from fastapi.responses import JSONResponse
from app.postgres import get_session
from app.redis import get_cache
from app.models.user_model import User, UserRole
from app.models.setting_model import Setting
from app.schemas.setting_list_schema import (
    SettingListResponse)
from app.repository import Repository
from app.hook import Hook, HOOK_AFTER_SETTING_LIST
from app.auth import auth

router = APIRouter()


@router.get("/settings", summary="Retrieve a list of settings.",
            response_class=JSONResponse, status_code=status.HTTP_200_OK,
            response_model=SettingListResponse, tags=["Settings"])
async def setting_list(
    request: Request,
    session=Depends(get_session), cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.admin))
) -> SettingListResponse:
    """
    Retrieve a list of settings. Fetches all existing settings from
    the repository. Each setting is returned as a key-value pair
    representing the configuration options for the app.

    **Auth:**
    - The token must be included in the request header and contain auth
    data for an active user with the `admin` role.

    **Returns:**
    - `SettingListResponse`: Contains a dictionary of settings where
    each key is a setting name and each value is its corresponding value.

    **Responses:**
    - `200 OK`: If the settings are successfully retrieved.
    - `401 Unauthorized`: If the token is invalid or lacks permissions.
    - `403 Forbidden`: If the token or secret key is missing.
    - `423 Locked`: If the app is locked.

    **Hooks:**
    - `HOOK_AFTER_SETTING_LIST`: Executes after the settings are
    successfully fetched.
    """
    settings_repository = Repository(session, cache, Setting)
    settings = await settings_repository.select_all()

    hook = Hook(request.app, session, cache, current_user=current_user)
    await hook.call(HOOK_AFTER_SETTING_LIST, settings)

    return {
        "settings": {x.setting_key: x.setting_value for x in settings},
    }
