# tests/routers/test_variable_delete.py
# SPDX-License-Identifier: GPL-3.0-only

import unittest
from unittest.mock import AsyncMock, MagicMock, patch


from tests.helpers import set_minimal_app_config_env


set_minimal_app_config_env()

from fastapi import status  # noqa: E402
from app.routers.variable_delete import variable_delete_router  # noqa: E402
from app.schemas.variable_path import VariablePath  # noqa: E402


class TestVariableDeleteRouter(unittest.IsolatedAsyncioTestCase):
    async def test_delete_returns_204(self):
        path = VariablePath(namespace="ns", variable_key="k")
        session = MagicMock()
        user = MagicMock()

        with patch(
            "app.routers.variable_delete.delete_variable",
            new_callable=AsyncMock,
        ) as mock_svc:
            response = await variable_delete_router(
                path=path,
                session=session,
                current_user=user,
            )

        mock_svc.assert_awaited_once_with(
            session=session,
            path=path,
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT,
        )
