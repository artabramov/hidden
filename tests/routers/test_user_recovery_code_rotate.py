# tests/routers/test_user_recovery_code_rotate.py
# SPDX-License-Identifier: GPL-3.0-only

import unittest
from unittest.mock import AsyncMock, MagicMock, patch

from tests.helpers import set_minimal_app_config_env


set_minimal_app_config_env()

from app.models.user import User  # noqa: E402
from app.routers.user_recovery_code_rotate import (  # noqa: E402
    user_recovery_code_rotate_router,
)
from app.schemas.user_recovery_code_rotate import (  # noqa: E402
    UserRecoveryCodeRotateRequest,
    UserRecoveryCodeRotateResponse,
)


class TestUserRecoveryCodeRotateRouter(unittest.IsolatedAsyncioTestCase):

    async def test_returns_200_and_calls_service(self):
        session = AsyncMock()
        current_user = MagicMock(spec=User)

        data = UserRecoveryCodeRotateRequest(
            recovery_code="ABCD-ABCD-ABCD-ABCD-ABCD-ABCD",
        )

        with patch(
            "app.routers.user_recovery_code_rotate.rotate_recovery_code",
            new_callable=AsyncMock,
            return_value="WXYZ-WXYZ-WXYZ-WXYZ-WXYZ-WXYZ",
        ) as mock_service:
            response = await user_recovery_code_rotate_router(
                data=data,
                session=session,
                current_user=current_user,
            )

        mock_service.assert_awaited_once_with(
            session=session,
            user=current_user,
            data=data,
        )

        self.assertIsInstance(response, UserRecoveryCodeRotateResponse)
        self.assertEqual(
            response.recovery_code,
            "WXYZ-WXYZ-WXYZ-WXYZ-WXYZ-WXYZ",
        )

        session.commit.assert_not_called()
        session.rollback.assert_not_called()
