# app/routers/user_list.py
# SPDX-License-Identifier: GPL-3.0-only

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.auth import AccessLevel, require_access
from app.dependencies.session import get_session
from app.models.user import User
from app.schemas.user_list import (
    USER_LIST_ERRORS,
    UserListRequest,
    UserListResponse,
)
from app.services.user_list import list_users

router = APIRouter(tags=["Users"])


@router.get(
    "/users",
    response_model=UserListResponse,
    responses=USER_LIST_ERRORS,
    status_code=status.HTTP_200_OK,
    summary="List users (filtered, paginated)",
)
async def user_list_router(
    session: AsyncSession = Depends(get_session),
    params: UserListRequest = Depends(),
    current_user: User = Depends(require_access(AccessLevel.ADMIN)),
) -> UserListResponse:
    """
    Returns a filtered list of users with pagination and ordering.
    It allows an administrator to retrieve user records that match
    the provided query parameters.

    **Hooks:**

    `USER_LIST_COMPLETED` — executed after the user list is retrieved.

    **Authentication:**

    - Requires a valid token with admin access.

    **Request query:**

    `UserListRequest` — pagination, ordering, and optional filters.

    **Response:**

    `UserListResponse` — current page of users and total count of users
    matching the filters (before pagination).

    **Response codes:**

    - `200` — User list returned successfully.
    - `401` — Invalid, expired, or missing token.
    - `403` — User not admin, inactive, or blocked.
    - `422` — Input values failed validation.
    - `503` — Service temporarily unavailable.
    """
    users, users_count = await list_users(
        session=session,
        params=params,
    )
    return UserListResponse(users=users, users_count=users_count)
