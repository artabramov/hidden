# app/routers/user_register.py
# SPDX-License-Identifier: GPL-3.0-only

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.session import get_session
from app.schemas.user_register import (
    USER_REGISTER_ERRORS,
    UserRegisterRequest,
    UserRegisterResponse,
)
from app.services.user_register import register_user

router = APIRouter(tags=["Authentication"])


@router.post(
    "/auth/register",
    response_model=UserRegisterResponse,
    responses=USER_REGISTER_ERRORS,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
)
async def user_register_router(
    data: UserRegisterRequest,
    session: AsyncSession = Depends(get_session),
) -> UserRegisterResponse:
    """
    Creates a new user account. It stores the provided credentials for
    a unique username and rejects the request if a user with the same
    username already exists.

    If this is the first registered user, the account is activated
    and assigned the admin role. All subsequent users are created as
    inactive with the default reader role and must be activated by
    an admin. Inactive users cannot authenticate until activated.

    The returned TOTP secret must be stored by the client and used to
    configure an authenticator application. The returned recovery code
    is shown only here and must be stored by the client; the server
    keeps a hash for later verification.

    **Hooks:**

    `USER_REGISTER_COMPLETED` — executed immediately after the user is
    successfully created.

    **Request body:**

    `UserRegisterRequest` — username, password, display name, and
    optional summary.

    **Response:**

    `UserRegisterResponse` — newly created user ID, TOTP secret for
    initial authenticator setup, and recovery code (save offline).

    **Response codes:**

    - `201` — User created successfully.
    - `422` — Input values failed validation.
    - `429` — Too many registration attempts.
    - `503` — Service temporarily unavailable.
    """
    user, totp_secret, recovery_code = await register_user(
        session=session,
        data=data,
    )
    return UserRegisterResponse(
        user_id=user.id,
        totp_secret=totp_secret,
        recovery_code=recovery_code,
    )
