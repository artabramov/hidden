# tests/routers/test_cipherdir_mount.py
# SPDX-License-Identifier: GPL-3.0-only

import unittest
from unittest.mock import AsyncMock, patch


from tests.helpers import set_minimal_app_config_env


set_minimal_app_config_env()

from app.routers.cipherdir_mount import mount_cipherdir_router  # noqa: E402
from app.schemas.cipherdir_mount import CipherdirMountRequest  # noqa: E402


class TestCipherdirMountRouter(unittest.IsolatedAsyncioTestCase):

    async def test_returns_204_and_calls_service(self):
        data = CipherdirMountRequest(
            master_password="Master-passphrase1",
        )

        with patch(
            "app.routers.cipherdir_mount.mount_cipherdir",
            new_callable=AsyncMock,
        ) as mock_service:
            response = await mount_cipherdir_router(
                data=data,
            )

        mock_service.assert_awaited_once_with(
            master_password="Master-passphrase1",
        )

        self.assertEqual(response.status_code, 204)
