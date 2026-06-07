# tests/routers/test_variable_get.py
# SPDX-License-Identifier: SSPL-1.0

import unittest
from unittest.mock import AsyncMock, MagicMock, patch


from tests.helpers import set_minimal_app_config_env


set_minimal_app_config_env()

from app.routers.variable_get import variable_get_router  # noqa: E402
from app.schemas.variable_path import VariablePath  # noqa: E402


class TestVariableGetRouter(unittest.IsolatedAsyncioTestCase):
    async def test_returns_variable(self):
        path = VariablePath(namespace="ns", variable_key="k")
        session = MagicMock()
        user = MagicMock()
        variable = MagicMock()

        with patch(
            "app.routers.variable_get.get_variable_service",
            new_callable=AsyncMock,
            return_value=variable,
        ) as mock_svc:
            out = await variable_get_router(
                path=path,
                session=session,
                current_user=user,
            )

        mock_svc.assert_awaited_once_with(
            session=session,
            path=path,
        )
        self.assertEqual(out, variable)
