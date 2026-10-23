# tests/routers/test_gocryptfs_reveal.py
# SPDX-License-Identifier: Apache-2.0

import unittest
from unittest.mock import AsyncMock, patch

from app.routers.gocryptfs_reveal import gocryptfs_reveal_router, router
from app.schemas.gocryptfs_auth import GocryptfsAuthRequest
from app.schemas.gocryptfs_reveal import GocryptfsRevealResponse

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


class TestGocryptfsRevealRouter(unittest.IsolatedAsyncioTestCase):
    def test_exposes_reveal_route(self):
        self.assertEqual(len(router.routes), 1)
        route = router.routes[0]

        self.assertEqual(route.path, "/gocryptfs/reveal")
        self.assertEqual(route.methods, {"POST"})
        self.assertEqual(route.status_code, 200)
        self.assertEqual(
            _requirement_flags(route),
            {
                "require_cipherdir": True,
                "require_mountpoint": None,
                "require_passphrase": True,
            },
        )

    async def test_returns_storage_secrets(self):
        data = GocryptfsAuthRequest(master_password=_PASSWORD)

        with patch(
            "app.routers.gocryptfs_reveal.gocryptfs_reveal",
            new=AsyncMock(
                return_value=("passphrase", "access", "secret"),
            ),
        ) as service:
            result = await gocryptfs_reveal_router(data)

        service.assert_awaited_once_with(master_password=_PASSWORD)
        self.assertEqual(
            result,
            GocryptfsRevealResponse(
                gocryptfs_passphrase="passphrase",
                versity_access_key="access",
                versity_secret_key="secret",
            ),
        )
