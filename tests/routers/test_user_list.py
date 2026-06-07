# tests/routers/test_user_list.py
# SPDX-License-Identifier: SSPL-1.0

import unittest
from unittest.mock import AsyncMock, MagicMock, patch


from tests.helpers import set_minimal_app_config_env


set_minimal_app_config_env()

from app.models.user import User  # noqa: E402
from app.routers.user_list import user_list_router  # noqa: E402
from app.schemas.user_list import UserListRequest  # noqa: E402


class TestUserListRouter(unittest.IsolatedAsyncioTestCase):

    async def test_returns_user_list_response(self):
        session = AsyncMock()
        current_user = MagicMock(spec=User)
        params = UserListRequest()

        user = MagicMock()
        user.id = 1
        user.username = "admin"
        user.role = "admin"
        user.display_name = "Admin User"
        user.summary = ""
        user.is_active = True
        user.is_blocked = False
        user.created_at = 1000
        user.updated_at = 1000

        with patch(
            "app.routers.user_list.list_users",
            new_callable=AsyncMock,
            return_value=([user], 1),
        ) as mock_service:
            result = await user_list_router(
                session=session,
                params=params,
                current_user=current_user,
            )

        mock_service.assert_awaited_once_with(
            session=session,
            params=params,
        )

        self.assertEqual(result.users_count, 1)
        self.assertEqual(len(result.users), 1)

        result_user = result.users[0]
        self.assertEqual(result_user.user_id, 1)
        self.assertEqual(result_user.username, "admin")
        self.assertEqual(result_user.role, "admin")
        self.assertEqual(result_user.display_name, "Admin User")
        self.assertEqual(result_user.summary, "")
        self.assertTrue(result_user.is_active)
