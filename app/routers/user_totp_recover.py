# app/routers/user_totp_recover.py
# SPDX-License-Identifier: GPL-3.0-only

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.session import get_session
from app.schemas.user_totp_recover import (
    USER_TOTP_RECOVER_ERRORS,
    UserTotpRecoverRequest,
    UserTotpRecoverResponse,
)
from app.services.user_totp_recover import recover_totp

router = APIRouter(tags=["Authentication"])


@router.post(
    "/auth/totp",
    response_model=UserTotpRecoverResponse,
    responses=USER_TOTP_RECOVER_ERRORS,
    status_code=status.HTTP_200_OK,
    summary="Reset TOTP secret using recovery code",
)
async def user_totp_recover_router(
    data: UserTotpRecoverRequest,
    session: AsyncSession = Depends(get_session),
) -> UserTotpRecoverResponse:
    """
    Alternate second step after password login. Verifies the recovery
    code for the MFA session, invalidates JTI, rotates the TOTP secret,
    and returns the new secret. Does not return an auth token.

    After too many failed recovery attempts, MFA state is cleared and the
    user must start from step 1 (same suspension window as failed TOTP).
    """
    user_id, totp_secret = await recover_totp(
        session=session,
        data=data,
    )
    return UserTotpRecoverResponse(
        user_id=user_id,
        totp_secret=totp_secret,
    )
