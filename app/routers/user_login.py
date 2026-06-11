# app/routers/user_login.py
# SPDX-License-Identifier: GPL-3.0-only

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.session import get_session
from app.schemas.user_login import (
    USER_LOGIN_ERRORS,
    UserLoginRequest,
    UserLoginResponse,
)
from app.services.user_login import login_user

router = APIRouter(tags=["Authentication"])


@router.post(
    "/auth/login",
    responses=USER_LOGIN_ERRORS,
    status_code=status.HTTP_200_OK,
    summary="Authentication step 1 (login by username and password)",
)
async def user_login_router(
    data: UserLoginRequest,
    session: AsyncSession = Depends(get_session),
) -> UserLoginResponse:
    """
    Performs the first step of user authentication. It validates the
    provided username and password, checks account status restrictions,
    and records successful password verification for subsequent
    second-factor (TOTP) verification. On failure, it increments the
    failed-attempts counter and may apply a temporary suspension.

    The verification result is stored as a short-lived timestamp used
    to authorize the MFA second-factor step.

    **Hooks:**

    `USER_LOGIN_COMPLETED` — executed immediately after successful
    credential verification.

    **Request body:**

    `UserLoginRequest` — username and password.

    **Response:**

    `UserLoginResponse` — temporary MFA session UUID used for the
    second authentication step.

    **Response codes:**

    - `200` — Password verification completed, MFA session started.
    - `422` — Input values failed validation.
    - `503` — Service temporarily unavailable.
    """
    mfa_session_uuid = await login_user(
        session=session,
        data=data,
    )
    return UserLoginResponse(
        mfa_session_uuid=mfa_session_uuid,
    )
