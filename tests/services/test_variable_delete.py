# tests/services/test_variable_delete.py
# SPDX-License-Identifier: SSPL-1.0

import unittest
from unittest.mock import AsyncMock, MagicMock, patch

from app.errors import ResourceNotFoundError
from app.events import Events as E
from app.models.variable import Variable
from app.schemas.variable_path import VariablePath
from app.services.variable_delete import delete_variable


class TestVariableDelete(unittest.IsolatedAsyncioTestCase):
    async def test_deletes_existing_variable(self):
        session = AsyncMock()
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
        repository.delete = AsyncMock()
        repository.commit = AsyncMock()

        with (
            patch(
                "app.services.variable_delete.ORMRepository",
                return_value=repository,
            ),
            patch(
                "app.services.variable_delete.hooks.emit",
                new_callable=AsyncMock,
            ) as mock_emit,
            patch(
                "app.services.variable_delete.write_audit",
                new=AsyncMock(),
            ) as write_audit_mock,
        ):
            out = await delete_variable(
                session=session,
                path=path,
            )

        self.assertIsNone(out)
        repository.select.assert_awaited_once_with(
            Variable,
            namespace="thumbnails",
            variable_key="max_width",
        )
        mock_emit.assert_awaited_once_with(
            E.VARIABLE_DELETE_COMPLETED,
            session,
            variable,
        )
        repository.delete.assert_awaited_once_with(variable)
        write_audit_mock.assert_awaited_once()
        repository.commit.assert_awaited_once()

    async def test_raises_not_found_when_variable_missing(self):
        session = AsyncMock()
        path = VariablePath(
            namespace="thumbnails",
            variable_key="max_width",
        )

        repository = MagicMock()
        repository.select = AsyncMock(return_value=None)
        repository.delete = AsyncMock()
        repository.commit = AsyncMock()

        with (
            patch(
                "app.services.variable_delete.ORMRepository",
                return_value=repository,
            ),
            patch(
                "app.services.variable_delete.hooks.emit",
                new_callable=AsyncMock,
            ) as mock_emit,
        ):
            with self.assertRaises(ResourceNotFoundError):
                await delete_variable(
                    session=session,
                    path=path,
                )

        repository.select.assert_awaited_once_with(
            Variable,
            namespace="thumbnails",
            variable_key="max_width",
        )
        mock_emit.assert_not_awaited()
        repository.delete.assert_not_awaited()
        repository.commit.assert_not_awaited()
