# tests/routers/test_variable_list.py
# SPDX-License-Identifier: SSPL-1.0

import unittest
from unittest.mock import AsyncMock, MagicMock, patch

from app.schemas.variable_namespace import VariableNamespace


from tests.helpers import set_minimal_app_config_env


set_minimal_app_config_env()

from app.routers.variable_list import variable_list_router  # noqa: E402


class TestVariableListRouter(unittest.IsolatedAsyncioTestCase):
    async def test_returns_variables_for_namespace(self):
        session = MagicMock()
        user = MagicMock()
        variables = [MagicMock(), MagicMock()]
        path = VariableNamespace(namespace="thumbnails")

        with patch(
            "app.routers.variable_list.list_variables",
            new_callable=AsyncMock,
            return_value=variables,
        ) as mock_service:
            out = await variable_list_router(
                path=path,
                session=session,
                current_user=user,
            )

        self.assertEqual(out, variables)
        mock_service.assert_awaited_once_with(
            session=session,
            namespace="thumbnails",
        )
