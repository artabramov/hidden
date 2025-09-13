"""FastAPI router for retrieving user details."""

from fastapi import APIRouter, Depends, status, Request, Path
from fastapi.responses import JSONResponse
from app.sqlite import get_session
from app.redis import get_cache
from app.models.user import User, UserRole
from app.schemas.user_select import UserSelectResponse
from app.error import E, LOC_PATH, ERR_VALUE_NOT_FOUND
from app.hook import Hook, HOOK_AFTER_USER_SELECT
from app.auth import auth
from app.repository import Repository

router = APIRouter()


@router.get("/user/{user_id}", summary="Retrieve user",
            response_class=JSONResponse, status_code=status.HTTP_200_OK,
            response_model=UserSelectResponse, tags=["Users"])
async def user_select(
    request: Request, user_id: int = Path(..., ge=1),
    session=Depends(get_session), cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.reader))
) -> UserSelectResponse:
    """
    Retrieves a single user by ID and returns their details.

    **Authentication:**
    - Requires a valid bearer token with `reader` role or higher.

    **Validation schemas:**
    - `UserSelectResponse` — user details: ID, account creation and
    last-login times, role, active status, username, first and last
    name, optional summary.

    **Path parameters:**
    - `user_id` (integer) — unique user identifier.

    **Response codes:**
    - `200` — user found; details returned.
    - `401` — missing, invalid, or expired token.
    - `403` — insufficient role, invalid JTI, user is inactive or
    suspended.
    - `404` — user not found.
    - `423` — application is temporarily locked.
    - `498` — secret key is missing.
    - `499` — secret key is invalid.

    **Hooks:**
    - `HOOK_AFTER_USER_SELECT`: executes after successful retrieval.
    """
    config = request.app.state.config

    user_repository = Repository(session, cache, User, config)
    user = await user_repository.select(id=user_id)

    if not user:
        raise E([LOC_PATH, "user_id"], user_id,
                ERR_VALUE_NOT_FOUND, status.HTTP_404_NOT_FOUND)

    hook = Hook(request, session, cache, current_user=current_user)
    await hook.call(HOOK_AFTER_USER_SELECT, user)

    request.state.log.debug("user retrieved; user_id=%s;", user.id)
    return await user.to_dict()
