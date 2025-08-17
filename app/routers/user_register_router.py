from fastapi import APIRouter, Depends, status, Request
from fastapi.responses import JSONResponse
from app.postgres import get_session
from app.redis import get_cache
from app.models.user_model import User, UserRole
from app.schemas.user_register_schema import (
    UserRegisterRequest, UserRegisterResponse)
from app.repository import Repository
from app.helpers.encrypt_helper import hash_str
from app.error import E, LOC_BODY, ERR_VALUE_EXISTS
from app.hook import Hook, HOOK_AFTER_USER_REGISTER

router = APIRouter()


@router.post("/user", summary="Register a new user.",
             response_class=JSONResponse, status_code=status.HTTP_201_CREATED,
             response_model=UserRegisterResponse, tags=["Users"])
async def user_register(
    schema: UserRegisterRequest, request: Request,
    session=Depends(get_session), cache=Depends(get_cache)
) -> UserRegisterResponse:
    """
    Registers a new user. Checks if the username is unique, and creates
    a new user with the provided details and credentials. If this is
    the first registered user, then he is active and gets the admin
    role. Otherwise, this user is created inactive with the reader
    role and should be activated by admin user.

    **Auth:**
    - No authentication required.

    **Returns:**
    - `UserRegisterResponse`: Response on success.

    **Responses:**
    - `201 Created`: If the user is successfully created.
    - `403 Forbidden`: If the secret key is missing.
    - `422 Unprocessable Entity`: If parameters validation fails.
    - `423 Locked`: If the app is locked.

    **Hooks:**
    - `HOOK_AFTER_USER_REGISTER`: Executes after the user is
    successfully created.
    """
    user_repository = Repository(session, cache, User)

    username_hash = hash_str(schema.username)
    user_exists = await user_repository.exists(username_hash__eq=username_hash)

    if user_exists:
        raise E([LOC_BODY, "username"], schema.username,
                ERR_VALUE_EXISTS, status.HTTP_422_UNPROCESSABLE_ENTITY)

    is_active = False
    user_role = UserRole.reader

    users_count = await user_repository.count_all()
    if users_count == 0:
        is_active = True
        user_role = UserRole.admin

    user = User(schema.username, schema.password, schema.first_name,
                schema.last_name, is_active=is_active, user_role=user_role,
                user_summary=schema.user_summary)
    await user_repository.insert(user)

    hook = Hook(request.app, session, cache, current_user=user)
    await hook.call(HOOK_AFTER_USER_REGISTER)

    return {
        "user_id": user.id,
        "mfa_secret": user.mfa_secret,
    }
