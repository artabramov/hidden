# tests/routers/test_lockdown_disable.py
# SPDX-License-Identifier: GPL-3.0-only

import unittest
from unittest.mock import AsyncMock, patch


from tests.helpers import set_minimal_app_config_env


set_minimal_app_config_env()

from app.routers.lockdown_disable import disable_lockdown_router  # noqa: E402
from app.schemas.lockdown_disable import LockdownDisableRequest  # noqa: E402


class TestLockdownDisableRouter(unittest.IsolatedAsyncioTestCase):

    async def test_returns_204_and_calls_service(self):
        data = LockdownDisableRequest(
            master_password="Master-passphrase1",
        )

        with patch(
            "app.routers.lockdown_disable.disable_lockdown",
            new_callable=AsyncMock,
        ) as mock_service:
            response = await disable_lockdown_router(
                data=data,
            )

        mock_service.assert_awaited_once_with(
            master_password="Master-passphrase1",
        )

        self.assertEqual(response.status_code, 204)
