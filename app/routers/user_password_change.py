# app/routers/user_password_change.py
# SPDX-License-Identifier: SSPL-1.0

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.auth import AccessLevel, require_access
from app.dependencies.session import get_session
from app.models.user import User
from app.schemas.user_password_change import (
    USER_PASSWORD_CHANGE_ERRORS,
    UserPasswordChangeRequest,
)
from app.services.user_password_change import change_password

router = APIRouter(tags=["Users"])


@router.patch(
    "/user/password",
    responses=USER_PASSWORD_CHANGE_ERRORS,
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Change current user password",
)
async def user_password_change_router(
    data: UserPasswordChangeRequest,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_access(AccessLevel.READ)),
) -> Response:
    """
    Changes the password of the currently authenticated user.
    It verifies the provided current password and stores the new
    password for the same account.

    **Hooks:**

    `USER_PASSWORD_CHANGE_COMPLETED` — executed after password change
    completes.

    **Authentication:**

    - Requires a valid token with read access or higher.

    **Request body:**

    `UserPasswordChangeRequest` — current and changed password.

    **Response:**

    Empty response body.

    **Response codes:**

    - `204` — User password changed successfully.
    - `401` — Invalid, expired, or missing token.
    - `403` — User inactive or blocked.
    - `422` — Input values failed validation.
    - `503` — Service temporarily unavailable.
    """
    await change_password(
        session=session,
        user=current_user,
        data=data,
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)
