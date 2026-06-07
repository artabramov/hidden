# tests/routers/test_user_select.py
# SPDX-License-Identifier: SSPL-1.0

import unittest
from unittest.mock import AsyncMock, MagicMock, patch


from tests.helpers import set_minimal_app_config_env


set_minimal_app_config_env()

from app.models.user import User  # noqa: E402
from app.routers.user_select import user_select_router  # noqa: E402


class TestUserSelectRouter(unittest.IsolatedAsyncioTestCase):

    async def test_returns_user_select_response(self):
        session = AsyncMock()
        current_user = MagicMock(spec=User)

        user = MagicMock()
        user.id = 1
        user.username = "admin"
        user.role = "admin"
        user.display_name = "Admin User"
        user.summary = ""
        user.is_active = True
        user.created_at = 1000
        user.last_authenticated_at = 1000

        with patch(
            "app.routers.user_select.select_user",
            new_callable=AsyncMock,
            return_value=user,
        ) as mock_service:
            result = await user_select_router(
                user_id=1,
                session=session,
                current_user=current_user,
            )

        mock_service.assert_awaited_once_with(
            session=session,
            current_user=current_user,
            user_id=1,
        )

        self.assertEqual(result.user_id, 1)
        self.assertEqual(result.username, "admin")
        self.assertEqual(result.role, "admin")
        self.assertEqual(result.display_name, "Admin User")
        self.assertEqual(result.summary, "")
        self.assertTrue(result.is_active)

        session.commit.assert_not_called()
        session.rollback.assert_not_called()
