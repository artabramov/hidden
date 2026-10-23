# tests/routers/test_gocryptfs_rotate.py
# SPDX-License-Identifier: Apache-2.0

import unittest
from unittest.mock import AsyncMock, patch

from fastapi import Response

from app.routers.gocryptfs_rotate import gocryptfs_rotate_router, router
from app.schemas.gocryptfs_rotate import GocryptfsRotateRequest

_CURRENT_PASSWORD = "current-password"
_CHANGED_PASSWORD = "Abcdefghijklmno1"


def _requirement_flags(route):
    dependency = route.dependencies[0].dependency
    return {
        name: cell.cell_contents
        for name, cell in zip(
            dependency.__code__.co_freevars,
            dependency.__closure__,
        )
    }


class TestGocryptfsRotateRouter(unittest.IsolatedAsyncioTestCase):
    def test_exposes_rotate_route(self):
        self.assertEqual(len(router.routes), 1)
        route = router.routes[0]

        self.assertEqual(route.path, "/gocryptfs/rotate")
        self.assertEqual(route.methods, {"POST"})
        self.assertEqual(route.status_code, 204)
        self.assertEqual(
            _requirement_flags(route),
            {
                "require_cipherdir": True,
                "require_mountpoint": None,
                "require_passphrase": True,
            },
        )

    async def test_rotates_master_password(self):
        data = GocryptfsRotateRequest(
            current_master_password=_CURRENT_PASSWORD,
            changed_master_password=_CHANGED_PASSWORD,
        )

        with patch(
            "app.routers.gocryptfs_rotate.gocryptfs_rotate",
            new=AsyncMock(),
        ) as service:
            result = await gocryptfs_rotate_router(data)

        service.assert_awaited_once_with(
            current_master_password=_CURRENT_PASSWORD,
            changed_master_password=_CHANGED_PASSWORD,
        )
        self.assertIsInstance(result, Response)
        self.assertEqual(result.status_code, 204)
