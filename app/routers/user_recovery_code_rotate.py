# app/routers/user_recovery_code_rotate.py
# SPDX-License-Identifier: SSPL-1.0

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.auth import AccessLevel, require_access
from app.dependencies.session import get_session
from app.models.user import User
from app.schemas.user_recovery_code_rotate import (
    USER_RECOVERY_CODE_ROTATE_ERRORS,
    UserRecoveryCodeRotateRequest,
    UserRecoveryCodeRotateResponse,
)
from app.services.user_recovery_code_rotate import rotate_recovery_code

router = APIRouter(tags=["Users"])


@router.patch(
    "/user/recovery",
    response_model=UserRecoveryCodeRotateResponse,
    responses=USER_RECOVERY_CODE_ROTATE_ERRORS,
    status_code=status.HTTP_200_OK,
    summary="Rotate current user recovery code",
)
async def user_recovery_code_rotate_router(
    data: UserRecoveryCodeRotateRequest,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_access(AccessLevel.READ)),
) -> UserRecoveryCodeRotateResponse:
    """
    Rotates the recovery code for the currently authenticated user after
    verifying the existing recovery code. The new code is returned once;
    the prior recovery code stops working.

    **Hooks:**

    `USER_RECOVERY_CODE_ROTATE_COMPLETED` — executed after recovery
    rotation completes.

    **Authentication:**

    - Requires a valid token with read access or higher.

    **Request body:**

    `UserRecoveryCodeRotateRequest` — current recovery code.

    **Response:**

    `UserRecoveryCodeRotateResponse` — new plaintext recovery code.

    **Response codes:**

    - `200` — Recovery code rotated; body contains the new code.
    - `401` — Invalid, expired, or missing token.
    - `403` — User inactive or blocked.
    - `422` — Validation failed or recovery code incorrect.
    - `503` — Service temporarily unavailable.
    """
    new_code = await rotate_recovery_code(
        session=session,
        user=current_user,
        data=data,
    )
    return UserRecoveryCodeRotateResponse(recovery_code=new_code)
