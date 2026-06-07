# tests/routers/test_user_token_invalidate.py
# SPDX-License-Identifier: SSPL-1.0

import unittest
from unittest.mock import AsyncMock, MagicMock, patch


from tests.helpers import set_minimal_app_config_env


set_minimal_app_config_env()

from app.models.user import User  # noqa: E402
from app.routers.user_token_invalidate import (  # noqa: E402
    user_token_invalidate_router,
)


class TestUserTokenInvalidateRouter(unittest.IsolatedAsyncioTestCase):

    async def test_returns_204_and_calls_service(self):
        session = AsyncMock()
        current_user = MagicMock(spec=User)

        with patch(
            "app.routers.user_token_invalidate.invalidate_token",
            new_callable=AsyncMock,
        ) as mock_service:
            response = await user_token_invalidate_router(
                session=session,
                current_user=current_user,
            )

        mock_service.assert_awaited_once_with(
            session=session,
            user=current_user,
        )

        self.assertEqual(response.status_code, 204)

        session.commit.assert_not_called()
        session.rollback.assert_not_called()
