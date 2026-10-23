# tests/routers/test_gocryptfs_health.py
# SPDX-License-Identifier: Apache-2.0

import unittest
from unittest.mock import AsyncMock, patch

from app.routers.gocryptfs_health import gocryptfs_health_router, router
from app.schemas.gocryptfs_health import GocryptfsHealthResponse


class TestGocryptfsHealthRouter(unittest.IsolatedAsyncioTestCase):
    def test_exposes_health_route(self):
        self.assertEqual(len(router.routes), 1)
        route = router.routes[0]

        self.assertEqual(route.path, "/gocryptfs/health")
        self.assertEqual(route.methods, {"GET"})
        self.assertEqual(route.status_code, 200)
        self.assertEqual(route.dependencies, [])

    async def test_returns_health_snapshot(self):
        health = {
            "is_cipherdir_created": True,
            "is_cipherdir_mounted": False,
            "is_versity_created": True,
            "is_versity_running": False,
            "is_watchdog_alive": True,
            "unix_timestamp": 100,
            "timezone_name": "UTC",
        }

        with patch(
            "app.routers.gocryptfs_health.gocryptfs_health",
            new=AsyncMock(return_value=health),
        ) as service:
            result = await gocryptfs_health_router()

        service.assert_awaited_once_with()
        self.assertEqual(result, GocryptfsHealthResponse(**health))
