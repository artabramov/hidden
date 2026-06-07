# app/routers/user_select.py
# SPDX-License-Identifier: SSPL-1.0

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.auth import AccessLevel, require_access
from app.dependencies.session import get_session
from app.models.user import User
from app.schemas.user_select import USER_SELECT_ERRORS, UserSelectResponse
from app.services.user_select import select_user

router = APIRouter(tags=["Users"])


@router.get(
    "/user/{user_id}",
    response_model=UserSelectResponse,
    responses=USER_SELECT_ERRORS,
    status_code=status.HTTP_200_OK,
    summary="Select user by ID",
)
async def user_select_router(
    user_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_access(AccessLevel.READ)),
) -> UserSelectResponse:
    """
    Returns user data for the specified user identifier. It retrieves
    the target user record if it exists and if the requesting user has
    sufficient access. Non-admin users can only access their own user.
    Admin users can access any user by ID.

    **Hooks:**

    `USER_SELECT_COMPLETED` — executed after user data is retrieved.

    **Authentication:**

    - Requires a valid token with read access or higher.

    **Request path:**

    - `user_id` — ID of the user to retrieve.

    **Response:**

    `UserSelectResponse` — identifier, username, display name, optional
    summary, role, activation flag, and creation / last-auth
    timestamps.

    **Response codes:**

    - `200` — User data returned successfully.
    - `401` — Invalid, expired, or missing token.
    - `403` — User inactive or blocked.
    - `404` — User not found.
    - `422` — Input values failed validation.
    - `503` — Service temporarily unavailable.
    """
    user = await select_user(
        session=session,
        current_user=current_user,
        user_id=user_id,
    )
    return UserSelectResponse.model_validate(user)
