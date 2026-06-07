# tests/routers/test_cipherdir_create.py
# SPDX-License-Identifier: SSPL-1.0

import unittest
from unittest.mock import AsyncMock, patch


from tests.helpers import set_minimal_app_config_env


set_minimal_app_config_env()

from app.routers.cipherdir_create import create_cipherdir_router  # noqa: E402
from app.schemas.cipherdir_create import CipherdirCreateRequest  # noqa: E402


class TestCipherdirCreateRouter(unittest.IsolatedAsyncioTestCase):

    async def test_returns_204_and_calls_service(self):
        data = CipherdirCreateRequest(master_password="Master-passphrase1")

        with patch(
            "app.routers.cipherdir_create.create_cipherdir",
            new_callable=AsyncMock,
        ) as mock_service:
            response = await create_cipherdir_router(data=data)

        mock_service.assert_awaited_once_with("Master-passphrase1")

        self.assertEqual(response.status_code, 204)
