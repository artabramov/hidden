# app/routers/user_role_change.py
# SPDX-License-Identifier: GPL-3.0-only

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.auth import AccessLevel, require_access
from app.dependencies.session import get_session
from app.models.user import User
from app.schemas.user_role_change import (
    USER_ROLE_CHANGE_ERRORS,
    UserRoleChangeRequest,
)
from app.services.user_role_change import change_user_role

router = APIRouter(tags=["Users"])


@router.patch(
    "/user/{user_id}/role",
    responses=USER_ROLE_CHANGE_ERRORS,
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Change role and active status by user ID",
)
async def user_role_change_router(
    user_id: int,
    data: UserRoleChangeRequest,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_access(AccessLevel.ADMIN)),
) -> Response:
    """
    Updates the role and active status of a target user. It is intended
    for administrative user management and does not allow an admin to
    modify own role or active state through this route.

    **Hooks:**

    `USER_ROLE_CHANGE_COMPLETED` — executed after role/status update
    completes.

    **Authentication:**

    - Requires a valid token with admin access.

    **Request path:**

    - `user_id` — target user ID.

    **Request body:**

    - `UserRoleChangeRequest` — role and active status values.

    **Response:**

    Empty response body.

    **Response codes:**

    - `204` — User role and status updated.
    - `401` — Invalid, expired, or missing token.
    - `403` — User inactive or blocked.
    - `404` — User not found.
    - `422` — Input values failed validation.
    - `503` — Service temporarily unavailable.
    """
    await change_user_role(
        session=session,
        current_user=current_user,
        user_id=user_id,
        data=data,
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)
