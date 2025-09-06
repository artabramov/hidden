"""FastAPI router for user registration."""

from fastapi import APIRouter, Depends, status, Request
from fastapi.responses import JSONResponse
from app.sqlite import get_session
from app.redis import get_cache
from app.models.user import User, UserRole
from app.repository import Repository
from app.helpers.jwt_helper import generate_jti
from app.helpers.mfa_helper import generate_mfa_secret
from app.managers.encryption_manager import EncryptionManager
from app.schemas.user_register import (
    UserRegisterRequest, UserRegisterResponse)
from app.hook import Hook, HOOK_AFTER_USER_REGISTER
from app.error import E, LOC_BODY, ERR_VALUE_EXISTS

router = APIRouter()


@router.post("/user", summary="Register user",
             response_class=JSONResponse, status_code=status.HTTP_201_CREATED,
             response_model=UserRegisterResponse, tags=["Users"])
async def user_register(
    request: Request, schema: UserRegisterRequest,
    session=Depends(get_session), cache=Depends(get_cache)
) -> UserRegisterResponse:
    """
    Registers a new user. Checks if the username is unique, and creates
    a new user with the provided details and credentials. If this is the
    first registered user, they are active and get the admin role;
    otherwise created as inactive reader and should be activated by
    an admin. On success triggers the post-register hook, and returns
    the user ID and one-time MFA secret.

    **Authentication:**
    - No prior authentication required.

    **Validation schemas:**
    - `UserRegisterRequest` — request body with username, password,
    first name, last name, and optional summary.
    - `UserRegisterResponse` — contains newly registered user ID and
    one-time MFA secret.

    **Request body**:
    - `username` (string, 2-40) — login identifier; automatically
    trimmed and lowercased; only Latin letters, digits, and underscore
    allowed.
    - `password` (string, ≥6) — login credential; must meet complexity
    rules — uppercase, lowercase, digit, special character; no
    whitespace.
    - `first_name` (string, 1-40) — given first name for the user
    profile; accepts any characters.
    - `last_name` (string, 1-40) — given name for the user profile;
    accepts any characters.
    - `summary` (string, ≤4096, optional) — profile description; accepts
    any characters.

    **Response codes:**
    - `201` — user successfully created.
    - `422` — validation failed or username already exists.
    - `423` — application is temporarily locked.
    - `498` — secret key is missing.
    - `499` — secret key is invalid.

    **Hooks:**
    - `HOOK_AFTER_USER_REGISTER`: Executes after the user is
    successfully created.
    """
    config = request.app.state.config
    encryption_manager = EncryptionManager(config, request.state.secret_key)

    user_repository = Repository(session, cache, User, config)
    user_exists = await user_repository.exists(username__eq=schema.username)

    if user_exists:
        raise E([LOC_BODY, "username"], schema.username,
                ERR_VALUE_EXISTS, status.HTTP_422_UNPROCESSABLE_ENTITY)

    active = False
    role = UserRole.reader

    users_count = await user_repository.count_all()
    if users_count == 0:
        active = True
        role = UserRole.admin

    password = schema.password.get_secret_value()
    password_hash = encryption_manager.get_hash(password)
    
    jti = generate_jti(config.JTI_LENGTH)
    jti_encrypted = encryption_manager.encrypt_str(jti)

    mfa_secret = generate_mfa_secret()
    mfa_secret_encrypted = encryption_manager.encrypt_str(mfa_secret)

    user = User(
        schema.username, password_hash, schema.first_name,
        schema.last_name, role, active, mfa_secret_encrypted,
        jti_encrypted, summary=schema.summary)

    await user_repository.insert(user)

    hook = Hook(request, session, cache, current_user=user)
    await hook.call(HOOK_AFTER_USER_REGISTER)

    request.state.log.debug("user registered; user_id=%s;", user.id)
    return {
        "user_id": user.id,
        "mfa_secret": mfa_secret,
    }
