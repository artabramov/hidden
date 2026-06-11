# tests/routers/test_user_role_change.py
# SPDX-License-Identifier: GPL-3.0-only

import unittest
from unittest.mock import AsyncMock, MagicMock, patch


from tests.helpers import set_minimal_app_config_env


set_minimal_app_config_env()

from app.models.user import User  # noqa: E402
from app.routers.user_role_change import user_role_change_router  # noqa: E402
from app.schemas.user_role_change import UserRoleChangeRequest  # noqa: E402


class TestUserRoleChangeRouter(unittest.IsolatedAsyncioTestCase):

    async def test_returns_204_and_calls_service(self):
        session = AsyncMock()
        current_user = MagicMock(spec=User)

        data = UserRoleChangeRequest(
            role="writer",
            is_active=True,
        )

        with patch(
            "app.routers.user_role_change.change_user_role",
            new_callable=AsyncMock,
        ) as mock_service:
            response = await user_role_change_router(
                user_id=42,
                data=data,
                session=session,
                current_user=current_user,
            )

        mock_service.assert_awaited_once_with(
            session=session,
            current_user=current_user,
            user_id=42,
            data=data,
        )

        self.assertEqual(response.status_code, 204)

        session.commit.assert_not_called()
        session.rollback.assert_not_called()
