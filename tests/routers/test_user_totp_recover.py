# tests/routers/test_user_totp_recover.py
# SPDX-License-Identifier: SSPL-1.0

import unittest
from unittest.mock import AsyncMock, patch

from tests.helpers import set_minimal_app_config_env


set_minimal_app_config_env()

from app.routers.user_totp_recover import (  # noqa: E402
    user_totp_recover_router,
)
from app.schemas.user_totp_recover import (  # noqa: E402
    UserTotpRecoverRequest,
)


class TestUserTotpRecoverRouter(unittest.IsolatedAsyncioTestCase):

    async def test_returns_user_totp_recover_response(self):
        session = AsyncMock()

        data = UserTotpRecoverRequest(
            mfa_session_uuid="session-" + "x" * 27,
            recovery_code="ABCD-ABCD-ABCD-ABCD-ABCD-ABCD",
        )

        with patch(
            "app.routers.user_totp_recover.recover_totp",
            new_callable=AsyncMock,
            return_value=(99, "NEWTOTP"),
        ) as mock_service:
            result = await user_totp_recover_router(
                data=data,
                session=session,
            )

        mock_service.assert_awaited_once_with(
            session=session,
            data=data,
        )

        self.assertEqual(result.user_id, 99)
        self.assertEqual(result.totp_secret, "NEWTOTP")
