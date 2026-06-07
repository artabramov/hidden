# tests/services/test_folder_select.py
# SPDX-License-Identifier: SSPL-1.0

import unittest
from unittest.mock import AsyncMock, MagicMock, patch

from app.errors import ResourceNotFoundError
from app.events import Events as E
from app.models.folder import Folder
from app.services.folder_select import select_folder


class TestSelectFolder(unittest.IsolatedAsyncioTestCase):

    async def test_returns_folder_with_recursive_flag_and_emits_hook(self):
        session = AsyncMock()

        folder = MagicMock(spec=Folder)
        folder.id = 42
        folder.is_write_protected_recursive.return_value = True

        parent_chain = [MagicMock(spec=Folder)]

        repository = AsyncMock()
        repository.select.return_value = folder
        repository.select_parent_chain.return_value = parent_chain

        with (
            patch(
                "app.services.folder_select.ORMRepository",
                return_value=repository,
            ),
            patch(
                "app.services.folder_select.hooks.emit",
                new=AsyncMock(),
            ) as emit_mock,
        ):
            result_folder, result_is_write_protected_recursive = (
                await select_folder(session, 42)
            )

        repository.select.assert_awaited_once_with(Folder, obj_id=42)
        repository.select_parent_chain.assert_awaited_once_with(folder)
        folder.is_write_protected_recursive.assert_called_once_with(
            parent_chain,
        )
        emit_mock.assert_awaited_once_with(
            E.FOLDER_SELECT_COMPLETED,
            session,
            folder,
        )
        self.assertIs(result_folder, folder)
        self.assertTrue(result_is_write_protected_recursive)

    async def test_raises_not_found_when_folder_does_not_exist(self):
        session = AsyncMock()

        repository = AsyncMock()
        repository.select.return_value = None

        with (
            patch(
                "app.services.folder_select.ORMRepository",
                return_value=repository,
            ),
            patch(
                "app.services.folder_select.hooks.emit",
                new=AsyncMock(),
            ) as emit_mock,
        ):
            with self.assertRaises(ResourceNotFoundError):
                await select_folder(session, 42)

        repository.select.assert_awaited_once_with(Folder, obj_id=42)
        repository.select_parent_chain.assert_not_awaited()
        emit_mock.assert_not_awaited()
