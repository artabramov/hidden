# tests/routers/test_health_check.py
# SPDX-License-Identifier: GPL-3.0-only

import unittest
from unittest.mock import AsyncMock, patch


class TestHealthCheckRouter(unittest.IsolatedAsyncioTestCase):

    async def test_returns_200_and_calls_service(self):
        payload = {
            "is_lockdown_mode_enabled": False,
            "is_first_admin_created": True,
            "is_cipherdir_created": True,
            "is_mountpoint_mounted": True,
            "is_watchdog_alive": True,
            "unix_timestamp": 123,
            "timezone_name": "UTC",
        }

        with patch(
            "app.routers.health_check.health_check",
            new=AsyncMock(return_value=payload),
        ) as mock_service:
            from app.routers.health_check import health_check_router

            response = await health_check_router()

        mock_service.assert_awaited_once_with()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.body.decode(),
            '{"is_lockdown_mode_enabled":false,'
            '"is_first_admin_created":true,'
            '"is_cipherdir_created":true,'
            '"is_mountpoint_mounted":true,'
            '"is_watchdog_alive":true,'
            '"unix_timestamp":123,'
            '"timezone_name":"UTC"}',
        )
