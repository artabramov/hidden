"""FastAPI router for user listing."""

from fastapi import APIRouter, Depends, status, Request
from fastapi.responses import JSONResponse
from app.sqlite import get_session
from app.redis import get_cache
from app.models.user import User, UserRole
from app.schemas.user_list import UserListRequest, UserListResponse
from app.hook import Hook, HOOK_AFTER_USER_LIST
from app.auth import auth
from app.repository import Repository

router = APIRouter()


@router.get("/users", summary="Retrieve list of users.",
            response_class=JSONResponse, status_code=status.HTTP_200_OK,
            response_model=UserListResponse, tags=["Users"])
async def user_list(
    request: Request, schema=Depends(UserListRequest),
    session=Depends(get_session), cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.reader))
) -> UserListResponse:
    """
    Retrieves a paginated list of users with optional filters and ordering.

    **Authentication:**
    - Requires a valid bearer token with `reader` role or higher.

    **Validation schemas:**
    - `UserListRequest` — pagination, ordering, and optional filters.
    - `UserListResponse` — list of users and total count.

    **Query parameters:**
    - Mapped from `UserListRequest` fields (offset, limit, order_by,
    order, and optional filter fields).

    **Response codes:**
    - `200` — list successfully retrieved.
    - `401` — missing, invalid, or expired token.
    - `403` — insufficient role, invalid JTI, user is inactive or
    suspended.
    - `423` — application is temporarily locked.
    - `498` — gocryptfs key is missing.
    - `499` — gocryptfs key is invalid.

    **Hooks:**
    - `HOOK_AFTER_USER_LIST`: executes after the list is retrieved.
    """
    config = request.app.state.config
    filters = schema.model_dump(exclude_none=True)

    user_repository = Repository(session, cache, User, config)
    users = await user_repository.select_all(**filters)
    users_count = await user_repository.count_all(**filters)

    hook = Hook(request, session, cache, current_user=current_user)
    await hook.call(HOOK_AFTER_USER_LIST, users, users_count)

    return {
        "users": [await user.to_dict() for user in users],
        "users_count": users_count,
    }
