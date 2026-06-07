# tests/services/test_variable_get.py
# SPDX-License-Identifier: SSPL-1.0

import unittest
from unittest.mock import AsyncMock, MagicMock, patch

from app.errors import ResourceNotFoundError
from app.events import Events as E
from app.models.variable import Variable
from app.schemas.variable_path import VariablePath
from app.services.variable_get import get_variable


class TestVariableGet(unittest.IsolatedAsyncioTestCase):
    async def test_returns_variable_when_found(self):
        session = MagicMock()
        path = VariablePath(
            namespace="thumbnails",
            variable_key="max_width",
        )
        variable = Variable(
            id=1,
            namespace="thumbnails",
            variable_key="max_width",
            variable_value="320",
            created_by=1,
        )

        repository = MagicMock()
        repository.select = AsyncMock(return_value=variable)

        with (
            patch(
                "app.services.variable_get.ORMRepository",
                return_value=repository,
            ),
            patch(
                "app.services.variable_get.hooks.emit",
                new_callable=AsyncMock,
            ) as mock_emit,
        ):
            out = await get_variable(
                session=session,
                path=path,
            )

        self.assertEqual(out, variable)
        repository.select.assert_awaited_once_with(
            Variable,
            namespace="thumbnails",
            variable_key="max_width",
        )
        mock_emit.assert_awaited_once_with(
            E.VARIABLE_GET_COMPLETED,
            session,
            variable,
        )

    async def test_raises_not_found_when_missing(self):
        session = MagicMock()
        path = VariablePath(
            namespace="thumbnails",
            variable_key="max_width",
        )

        repository = MagicMock()
        repository.select = AsyncMock(return_value=None)

        with (
            patch(
                "app.services.variable_get.ORMRepository",
                return_value=repository,
            ),
            patch(
                "app.services.variable_get.hooks.emit",
                new_callable=AsyncMock,
            ) as mock_emit,
        ):
            with self.assertRaises(ResourceNotFoundError):
                await get_variable(
                    session=session,
                    path=path,
                )

        repository.select.assert_awaited_once_with(
            Variable,
            namespace="thumbnails",
            variable_key="max_width",
        )
        mock_emit.assert_not_awaited()
