# tests/routers/test_user_register.py
# SPDX-License-Identifier: SSPL-1.0

import unittest
from unittest.mock import AsyncMock, MagicMock, patch


from tests.helpers import set_minimal_app_config_env


set_minimal_app_config_env()

from app.routers.user_register import user_register_router  # noqa: E402
from app.schemas.user_register import UserRegisterRequest  # noqa: E402


class TestUserRegisterRouter(unittest.IsolatedAsyncioTestCase):

    async def test_returns_user_register_response(self):
        session = AsyncMock()

        data = UserRegisterRequest(
            username="admin",
            password="Master-passphrase1",
            display_name="Admin User",
            summary="",
        )

        user = MagicMock()
        user.id = 42

        with patch(
            "app.routers.user_register.register_user",
            new_callable=AsyncMock,
            return_value=(user, "TOTPSECRET", "ABCD-ABCD-ABCD-ABCD-ABCD-ABCD"),
        ) as mock_service:
            result = await user_register_router(
                data=data,
                session=session,
            )

        mock_service.assert_awaited_once_with(
            session=session,
            data=data,
        )

        self.assertEqual(result.user_id, 42)
        self.assertEqual(result.totp_secret, "TOTPSECRET")
        self.assertEqual(result.recovery_code, "ABCD-ABCD-ABCD-ABCD-ABCD-ABCD")

        session.commit.assert_not_called()
        session.rollback.assert_not_called()
