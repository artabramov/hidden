# tests/routers/test_cipherdir_password_change.py
# SPDX-License-Identifier: GPL-3.0-only

import unittest
from unittest.mock import AsyncMock, patch


from tests.helpers import set_minimal_app_config_env


set_minimal_app_config_env()

from app.routers.cipherdir_password_change import (  # noqa: E402
    change_cipherdir_password_router,
)
from app.schemas.cipherdir_password_change import (  # noqa: E402
    CipherdirPasswordChangeRequest,
)


class TestCipherdirPasswordChangeRouter(unittest.IsolatedAsyncioTestCase):

    async def test_returns_204_and_calls_service(self):
        data = CipherdirPasswordChangeRequest(
            current_master_password="Master-passphrase1",
            changed_master_password="Another-master-passphrase1",
        )

        with patch(
            "app.routers.cipherdir_password_change.change_cipherdir_password",
            new_callable=AsyncMock,
        ) as mock_service:
            response = await change_cipherdir_password_router(
                data=data,
            )

        mock_service.assert_awaited_once_with(
            current_master_password="Master-passphrase1",
            changed_master_password="Another-master-passphrase1",
        )

        self.assertEqual(response.status_code, 204)
