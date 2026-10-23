# tests/routers/test_gocryptfs_init.py
# SPDX-License-Identifier: Apache-2.0

import unittest
from unittest.mock import AsyncMock, patch

from app.routers.gocryptfs_init import gocryptfs_init_router, router
from app.schemas.gocryptfs_init import (
    GocryptfsInitRequest,
    GocryptfsInitResponse,
)

_PASSWORD = "Abcdefghijklmno1"


def _requirement_flags(route):
    dependency = route.dependencies[0].dependency
    return {
        name: cell.cell_contents
        for name, cell in zip(
            dependency.__code__.co_freevars,
            dependency.__closure__,
        )
    }


class TestGocryptfsInitRouter(unittest.IsolatedAsyncioTestCase):
    def test_exposes_init_route(self):
        self.assertEqual(len(router.routes), 1)
        route = router.routes[0]

        self.assertEqual(route.path, "/gocryptfs/init")
        self.assertEqual(route.methods, {"POST"})
        self.assertEqual(route.status_code, 200)
        self.assertEqual(
            _requirement_flags(route),
            {
                "require_cipherdir": False,
                "require_mountpoint": False,
                "require_passphrase": False,
            },
        )

    async def test_returns_created_credentials(self):
        data = GocryptfsInitRequest(master_password=_PASSWORD)

        with patch(
            "app.routers.gocryptfs_init.gocryptfs_init",
            new=AsyncMock(return_value=("access", "secret")),
        ) as service:
            result = await gocryptfs_init_router(data)

        service.assert_awaited_once_with(_PASSWORD)
        self.assertEqual(
            result,
            GocryptfsInitResponse(
                access_key="access",
                secret_key="secret",
            ),
        )
