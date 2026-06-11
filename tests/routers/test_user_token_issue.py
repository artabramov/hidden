# tests/routers/test_user_token_issue.py
# SPDX-License-Identifier: GPL-3.0-only

import unittest
from unittest.mock import AsyncMock, patch


from tests.helpers import set_minimal_app_config_env


set_minimal_app_config_env()

from app.routers.user_token_issue import user_token_issue_router  # noqa: E402
from app.schemas.user_token_issue import TokenIssueRequest  # noqa: E402


class TestUserTokenIssueRouter(unittest.IsolatedAsyncioTestCase):

    async def test_returns_token_issue_response(self):
        session = AsyncMock()

        data = TokenIssueRequest(
            mfa_session_uuid="session-" + "x" * 27,
            totp="123456",
        )

        with patch(
            "app.routers.user_token_issue.issue_token",
            new_callable=AsyncMock,
            return_value=(42, "auth-token"),
        ) as mock_service:
            result = await user_token_issue_router(
                data=data,
                session=session,
            )

        mock_service.assert_awaited_once_with(
            session=session,
            data=data,
        )

        self.assertEqual(result.user_id, 42)
        self.assertEqual(result.auth_token, "auth-token")

        session.commit.assert_not_called()
        session.rollback.assert_not_called()
