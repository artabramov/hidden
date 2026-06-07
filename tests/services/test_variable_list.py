# tests/services/test_variable_list.py
# SPDX-License-Identifier: SSPL-1.0

import unittest
from unittest.mock import AsyncMock, MagicMock, patch

from app.events import Events as E
from app.models.variable import Variable
from app.services.variable_list import list_variables


class TestVariableList(unittest.IsolatedAsyncioTestCase):
    async def test_returns_variables_for_namespace(self):
        session = MagicMock()
        variables = [
            Variable(
                id=1,
                namespace="thumbnails",
                variable_key="max_width",
                variable_value="320",
                created_by=1,
            ),
            Variable(
                id=2,
                namespace="thumbnails",
                variable_key="quality",
                variable_value="80",
                created_by=1,
            ),
        ]

        repository = MagicMock()
        repository.select_all = AsyncMock(return_value=variables)

        with (
            patch(
                "app.services.variable_list.ORMRepository",
                return_value=repository,
            ),
            patch(
                "app.services.variable_list.hooks.emit",
                new_callable=AsyncMock,
            ) as mock_emit,
        ):
            out = await list_variables(
                session=session,
                namespace="thumbnails",
            )

        self.assertEqual(out, variables)
        repository.select_all.assert_awaited_once_with(
            Variable,
            namespace="thumbnails",
        )
        mock_emit.assert_awaited_once_with(
            E.VARIABLE_LIST_COMPLETED,
            session,
            variables,
        )

    async def test_returns_empty_list_when_namespace_has_no_variables(self):
        session = MagicMock()
        repository = MagicMock()
        repository.select_all = AsyncMock(return_value=[])

        with (
            patch(
                "app.services.variable_list.ORMRepository",
                return_value=repository,
            ),
            patch(
                "app.services.variable_list.hooks.emit",
                new_callable=AsyncMock,
            ) as mock_emit,
        ):
            out = await list_variables(
                session=session,
                namespace="missing_namespace",
            )

        self.assertEqual(out, [])
        repository.select_all.assert_awaited_once_with(
            Variable,
            namespace="missing_namespace",
        )
        mock_emit.assert_awaited_once_with(
            E.VARIABLE_LIST_COMPLETED,
            session,
            [],
        )
