from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from app.postgres import get_session
from app.redis import get_cache
from app.models.user_model import User, UserRole
from app.models.setting_model import Setting
from app.schemas.setting_insert_schema import (
    SettingInsertRequest, SettingInsertResponse)
from app.repository import Repository
from app.hook import Hook, HOOK_AFTER_SETTING_INSERT
from app.auth import auth
from app.helpers.encrypt_helper import hash_str

router = APIRouter()


@router.post("/setting", summary="Update a setting.",
             response_class=JSONResponse, status_code=status.HTTP_200_OK,
             response_model=SettingInsertResponse, tags=["Settings"])
async def setting_insert(
    schema: SettingInsertRequest,
    session=Depends(get_session), cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.admin))
) -> SettingInsertResponse:
    """
    Updates a setting. If the setting exists, its value will be updated.
    Otherwise, a new setting will be created. If the setting value is
    not provided, the setting will be deleted.

    **Auth:**
    - The token must be included in the request header and contain auth
    data for an active user with the`admin` role.

    **Returns:**
    - `SettingInsertResponse`: Contains the setting key.

    **Responses:**
    - `200 OK`: If the setting is successfully created, updated or
    deleted.
    - `401 Unauthorized`: If the token is invalid or lacks permissions.
    - `403 Forbidden`: If the token or secret key is missing.
    - `422 Unprocessable Entity`: If parameters validation fails.
    - `423 Locked`: If the app is locked.

    **Hooks:**
    - `HOOK_AFTER_SETTING_INSERT`: Executes after the setting is
    successfully created, updated or deleted.
    """
    setting_repository = Repository(session, cache, Setting)
    setting_key_hash = hash_str(schema.setting_key)
    setting = await setting_repository.select(
        setting_key_hash__eq=setting_key_hash)

    if not setting:
        setting = Setting(
            current_user.id, schema.setting_key, schema.setting_value)
        await setting_repository.insert(setting)

    elif setting and schema.setting_value:
        setting.setting_value = schema.setting_value
        await setting_repository.update(setting)

    else:
        await setting_repository.delete(setting)

    hook = Hook(session, cache, current_user=current_user)
    await hook.call(HOOK_AFTER_SETTING_INSERT, setting)

    return {"setting_key": setting.setting_key}
