# app/routers/user_update.py
# SPDX-License-Identifier: GPL-3.0-only

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.auth import AccessLevel, require_access
from app.dependencies.session import get_session
from app.models.user import User
from app.schemas.user_update import USER_UPDATE_ERRORS, UserUpdateRequest
from app.services.user_update import update_user

router = APIRouter(tags=["Users"])


@router.patch(
    "/user",
    responses=USER_UPDATE_ERRORS,
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Update current user profile",
)
async def user_update_router(
    data: UserUpdateRequest,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_access(AccessLevel.READ)),
) -> Response:
    """
    Updates profile fields of an existing user. It changes user data
    that does not affect authentication credentials or role assignment.

    **Hooks:**

    `USER_UPDATE_COMPLETED` — executed after profile data is updated.

    **Authentication:**

    - Requires a valid token with read access or higher.

    **Request body:**

    `UserUpdateRequest` — display name and optional summary.

    **Response:**

    Empty response body.

    **Response codes:**

    - `204` — User data updated successfully.
    - `401` — Invalid, expired, or missing token.
    - `403` — User inactive or blocked.
    - `422` — Input values failed validation.
    - `503` — Service temporarily unavailable.
    """
    await update_user(
        session=session,
        user=current_user,
        data=data,
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)
