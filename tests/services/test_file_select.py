# tests/services/test_file_select.py
# SPDX-License-Identifier: SSPL-1.0

import unittest
from unittest.mock import AsyncMock, MagicMock, patch

from app.errors import ResourceNotFoundError
from app.events import Events as E
from app.models.file import File
from app.services.file_select import select_file


class TestSelectFile(unittest.IsolatedAsyncioTestCase):

    async def test_returns_file_and_emits_hook(self):
        session = AsyncMock()

        file = MagicMock(spec=File)
        file.id = 42

        repository = AsyncMock()
        repository.select.return_value = file

        with (
            patch(
                "app.services.file_select.ORMRepository",
                return_value=repository,
            ),
            patch(
                "app.services.file_select.hooks.emit",
                new=AsyncMock(),
            ) as emit_mock,
        ):
            result = await select_file(session, 42)

        repository.select.assert_awaited_once_with(File, obj_id=42)
        emit_mock.assert_awaited_once_with(
            E.FILE_SELECT_COMPLETED,
            session,
            file,
        )
        self.assertIs(result, file)

    async def test_raises_not_found_when_file_does_not_exist(self):
        session = AsyncMock()

        repository = AsyncMock()
        repository.select.return_value = None

        with (
            patch(
                "app.services.file_select.ORMRepository",
                return_value=repository,
            ),
            patch(
                "app.services.file_select.hooks.emit",
                new=AsyncMock(),
            ) as emit_mock,
        ):
            with self.assertRaises(ResourceNotFoundError):
                await select_file(session, 42)

        repository.select.assert_awaited_once_with(File, obj_id=42)
        emit_mock.assert_not_awaited()
