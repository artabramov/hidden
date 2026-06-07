# app/routers/user_token_invalidate.py
# SPDX-License-Identifier: SSPL-1.0

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.auth import AccessLevel, require_access
from app.dependencies.session import get_session
from app.models.user import User
from app.schemas.user_token_invalidate import USER_TOKEN_INVALIDATE_ERRORS
from app.services.user_token_invalidate import invalidate_token

router = APIRouter(tags=["Authentication"])


@router.delete(
    "/auth/token",
    responses=USER_TOKEN_INVALIDATE_ERRORS,
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Invalidate the token",
)
async def user_token_invalidate_router(
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_access(AccessLevel.READ)),
) -> Response:
    """
    Invalidates the current authentication token. After successful
    completion, the token can no longer be used for authenticated
    requests.

    **Hooks:**

    `USER_TOKEN_INVALIDATE_COMPLETED` — executed after the token is
    invalidated.

    **Authentication:**

    - Requires a valid token with read access or higher.

    **Response:**

    Empty response body.

    **Response codes:**

    - `204` — Token invalidated successfully.
    - `401` — Invalid, expired, or missing token.
    - `403` — User inactive or blocked.
    - `503` — Service temporarily unavailable.
    """
    await invalidate_token(
        session=session,
        user=current_user,
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)
