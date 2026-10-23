# tests/routers/test_gocryptfs_mount.py
# SPDX-License-Identifier: Apache-2.0

import unittest
from unittest.mock import AsyncMock, patch

from fastapi import Response

from app.routers.gocryptfs_mount import gocryptfs_mount_router, router
from app.schemas.gocryptfs_auth import GocryptfsAuthRequest

_PASSWORD = "current-password"


def _requirement_flags(route):
    dependency = route.dependencies[0].dependency
    return {
        name: cell.cell_contents
        for name, cell in zip(
            dependency.__code__.co_freevars,
            dependency.__closure__,
        )
    }


class TestGocryptfsMountRouter(unittest.IsolatedAsyncioTestCase):
    def test_exposes_mount_route(self):
        self.assertEqual(len(router.routes), 1)
        route = router.routes[0]

        self.assertEqual(route.path, "/gocryptfs/mount")
        self.assertEqual(route.methods, {"POST"})
        self.assertEqual(route.status_code, 204)
        self.assertEqual(
            _requirement_flags(route),
            {
                "require_cipherdir": True,
                "require_mountpoint": False,
                "require_passphrase": True,
            },
        )

    async def test_mounts_storage(self):
        data = GocryptfsAuthRequest(master_password=_PASSWORD)

        with patch(
            "app.routers.gocryptfs_mount.gocryptfs_mount",
            new=AsyncMock(),
        ) as service:
            result = await gocryptfs_mount_router(data)

        service.assert_awaited_once_with(master_password=_PASSWORD)
        self.assertIsInstance(result, Response)
        self.assertEqual(result.status_code, 204)
