# tests/routers/test_lockdown_enable.py
# SPDX-License-Identifier: GPL-3.0-only

import unittest
from unittest.mock import AsyncMock, patch


from tests.helpers import set_minimal_app_config_env


set_minimal_app_config_env()

from app.routers.lockdown_enable import enable_lockdown_router  # noqa: E402
from app.schemas.lockdown_enable import LockdownEnableRequest  # noqa: E402


class TestLockdownEnableRouter(unittest.IsolatedAsyncioTestCase):

    async def test_returns_204_and_calls_service(self):
        data = LockdownEnableRequest(
            master_password="Master-passphrase1",
        )

        with patch(
            "app.routers.lockdown_enable.enable_lockdown",
            new_callable=AsyncMock,
        ) as mock_service:
            response = await enable_lockdown_router(
                data=data,
            )

        mock_service.assert_awaited_once_with(
            master_password="Master-passphrase1",
        )

        self.assertEqual(response.status_code, 204)
