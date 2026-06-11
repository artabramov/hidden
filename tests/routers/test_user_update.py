# tests/routers/test_user_update.py
# SPDX-License-Identifier: GPL-3.0-only

import unittest
from unittest.mock import AsyncMock, MagicMock, patch


from tests.helpers import set_minimal_app_config_env


set_minimal_app_config_env()

from app.models.user import User  # noqa: E402
from app.routers.user_update import user_update_router  # noqa: E402
from app.schemas.user_update import UserUpdateRequest  # noqa: E402


class TestUserUpdateRouter(unittest.IsolatedAsyncioTestCase):

    async def test_returns_204_and_calls_service(self):
        session = AsyncMock()
        current_user = MagicMock(spec=User)

        data = UserUpdateRequest(
            display_name="New Name",
            summary="Updated summary",
        )

        with patch(
            "app.routers.user_update.update_user",
            new_callable=AsyncMock,
        ) as mock_service:
            response = await user_update_router(
                data=data,
                session=session,
                current_user=current_user,
            )

        mock_service.assert_awaited_once_with(
            session=session,
            user=current_user,
            data=data,
        )

        self.assertEqual(response.status_code, 204)

        session.commit.assert_not_called()
        session.rollback.assert_not_called()
