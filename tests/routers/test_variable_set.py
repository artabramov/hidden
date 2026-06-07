# tests/routers/test_variable_set.py
# SPDX-License-Identifier: SSPL-1.0

import unittest
from unittest.mock import AsyncMock, MagicMock, patch


from tests.helpers import set_minimal_app_config_env


set_minimal_app_config_env()

from app.models.user import User  # noqa: E402
from app.routers.variable_set import variable_set_router  # noqa: E402
from app.schemas.variable_path import VariablePath  # noqa: E402
from app.schemas.variable_set import VariableSetRequest  # noqa: E402


class TestVariableSetRouter(unittest.IsolatedAsyncioTestCase):

    async def test_returns_204_and_calls_service(self):
        session = AsyncMock()
        current_user = MagicMock(spec=User)

        path = VariablePath(
            namespace="system",
            variable_key="theme",
        )
        data = VariableSetRequest(
            variable_value="dark",
        )

        with patch(
            "app.routers.variable_set.set_variable",
            new_callable=AsyncMock,
        ) as mock_service:
            response = await variable_set_router(
                data=data,
                path=path,
                session=session,
                current_user=current_user,
            )

        mock_service.assert_awaited_once_with(
            session=session,
            user=current_user,
            data=data,
            path=path,
        )

        self.assertEqual(response.status_code, 204)

        session.commit.assert_not_called()
        session.rollback.assert_not_called()
