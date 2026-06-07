# tests/routers/test_user_password_change.py
# SPDX-License-Identifier: SSPL-1.0

import unittest
from unittest.mock import AsyncMock, MagicMock, patch


from tests.helpers import set_minimal_app_config_env


set_minimal_app_config_env()

from app.models.user import User  # noqa: E402
from app.routers.user_password_change import (  # noqa: E402
    user_password_change_router,
)
from app.schemas.user_password_change import (  # noqa: E402
    UserPasswordChangeRequest,
)


class TestUserPasswordChangeRouter(unittest.IsolatedAsyncioTestCase):

    async def test_returns_204_and_calls_service(self):
        session = AsyncMock()
        current_user = MagicMock(spec=User)

        data = UserPasswordChangeRequest(
            current_password="Master-passphrase1",
            changed_password="Another-master-passphrase1",
        )

        with patch(
            "app.routers.user_password_change.change_password",
            new_callable=AsyncMock,
        ) as mock_service:
            response = await user_password_change_router(
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
