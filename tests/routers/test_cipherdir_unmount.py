# tests/routers/test_cipherdir_unmount.py
# SPDX-License-Identifier: SSPL-1.0

import unittest
from unittest.mock import AsyncMock, patch


from tests.helpers import set_minimal_app_config_env


set_minimal_app_config_env()

from app.routers.cipherdir_unmount import unmount_cipherdir_router  # noqa: E501, E402
from app.schemas.cipherdir_unmount import CipherdirUnmountRequest  # noqa: E402


class TestCipherdirUnmountRouter(unittest.IsolatedAsyncioTestCase):

    async def test_returns_204_and_calls_service(self):
        data = CipherdirUnmountRequest(
            master_password="Master-passphrase1",
        )

        with patch(
            "app.routers.cipherdir_unmount.unmount_cipherdir",
            new_callable=AsyncMock,
        ) as mock_service:
            response = await unmount_cipherdir_router(
                data=data,
            )

        mock_service.assert_awaited_once_with(
            master_password="Master-passphrase1",
        )

        self.assertEqual(response.status_code, 204)
