# app/routers/user_token_issue.py
# SPDX-License-Identifier: GPL-3.0-only

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.session import get_session
from app.schemas.user_token_issue import (
    USER_TOKEN_ISSUE_ERRORS,
    TokenIssueRequest,
    TokenIssueResponse,
)
from app.services.user_token_issue import issue_token

router = APIRouter(tags=["Authentication"])


@router.post(
    "/auth/token",
    response_model=TokenIssueResponse,
    responses=USER_TOKEN_ISSUE_ERRORS,
    status_code=status.HTTP_200_OK,
    summary="Authentication step 2 (issue token by session UUID and TOTP)",
)
async def user_token_issue_router(
    data: TokenIssueRequest,
    session: AsyncSession = Depends(get_session),
) -> TokenIssueResponse:
    """
    Performs the second step of user authentication. It verifies the
    provided TOTP code for a user identified by a temporary MFA session
    UUID and issues an authentication token.

    On success, it invalidates the MFA session, resets the password
    verification flag, and returns the user ID together with the issued
    auth token.

    On failure, it increments the failed-attempts counter. If the limit
    is reached, the user is temporarily suspended and must repeat the
    authentication flow from step 1 (password verification).

    Password and TOTP verification are linked by a short-lived MFA
    session UUID and password verification timestamp.

    **Hooks:**

    `USER_TOKEN_ISSUE_COMPLETED` — executed after a token is issued.

    **Request body:**

    `TokenIssueRequest` — MFA session UUID and TOTP code.

    **Response:**

    `TokenIssueResponse` — user ID and authentication token.

    **Response codes:**

    - `200` — Authentication token issued.
    - `409` — Password verification expired or missing.
    - `422` — Input values failed validation.
    - `503` — Service temporarily unavailable.
    """
    user_id, auth_token = await issue_token(
        session=session,
        data=data,
    )
    return TokenIssueResponse(
        user_id=user_id,
        auth_token=auth_token,
    )
