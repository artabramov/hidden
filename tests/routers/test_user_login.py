# tests/routers/test_user_login.py
# SPDX-License-Identifier: GPL-3.0-only

import unittest
from unittest.mock import AsyncMock, patch


from tests.helpers import set_minimal_app_config_env


set_minimal_app_config_env()

from app.routers.user_login import user_login_router  # noqa: E402
from app.schemas.user_login import (  # noqa: E402
    UserLoginRequest,
    UserLoginResponse,
)


class TestUserLoginRouter(unittest.IsolatedAsyncioTestCase):

    async def test_returns_user_login_response_and_calls_service(self):
        session = AsyncMock()
        data = UserLoginRequest(
            username="admin",
            password="Master-passphrase1",
        )

        with patch(
            "app.routers.user_login.login_user",
            new_callable=AsyncMock,
        ) as mock_service:
            mock_service.return_value = "mfa-session-from-service"
            result = await user_login_router(
                data=data,
                session=session,
            )

        mock_service.assert_awaited_once_with(
            session=session,
            data=data,
        )

        self.assertIsInstance(result, UserLoginResponse)
        self.assertEqual(result.mfa_session_uuid, "mfa-session-from-service")

        session.commit.assert_not_called()
        session.rollback.assert_not_called()
