# tests/services/test_folder_list.py
# SPDX-License-Identifier: GPL-3.0-only

import unittest
from unittest.mock import AsyncMock, MagicMock, patch

from app.errors import ResourceNotFoundError
from app.events import Events as E
from app.models.folder import Folder
from app.schemas.folder_list import FolderListRequest
from app.services.folder_list import list_folders


class TestListFolders(unittest.IsolatedAsyncioTestCase):

    async def test_lists_root_folders_and_emits_hook(self):
        session = AsyncMock()
        params = FolderListRequest(order_by="dirname", order="asc")

        folders = [MagicMock(spec=Folder), MagicMock(spec=Folder)]

        repository = AsyncMock()
        repository.count_all.return_value = 2
        repository.select_all.return_value = folders

        with (
            patch(
                "app.services.folder_list.ORMRepository",
                return_value=repository,
            ),
            patch(
                "app.services.folder_list.hooks.emit",
                new=AsyncMock(),
            ) as emit_mock,
        ):
            result_folders, result_count, result_recursive = (
                await list_folders(session, params)
            )

        repository.select.assert_not_awaited()
        repository.select_parent_chain.assert_not_awaited()
        repository.count_all.assert_awaited_once_with(
            Folder,
            order_by="dirname",
            order="asc",
            parent_id__is=None,
        )
        repository.select_all.assert_awaited_once_with(
            Folder,
            order_by="dirname",
            order="asc",
            parent_id__is=None,
        )
        emit_mock.assert_awaited_once_with(
            E.FOLDER_LIST_COMPLETED,
            session,
            folders,
        )

        self.assertEqual(result_folders, folders)
        self.assertEqual(result_count, 2)
        self.assertFalse(result_recursive)

    async def test_lists_child_folders_when_parent_exists(self):
        session = AsyncMock()
        params = FolderListRequest(
            order_by="created_at",
            order="desc",
            parent_id__eq=42,
        )

        parent = MagicMock(spec=Folder)
        parent.is_write_protected = False
        parent.is_write_protected_recursive.return_value = True
        parent_chain = [MagicMock(spec=Folder)]
        folders = [MagicMock(spec=Folder)]

        repository = AsyncMock()
        repository.select.return_value = parent
        repository.select_parent_chain.return_value = parent_chain
        repository.count_all.return_value = 1
        repository.select_all.return_value = folders

        with (
            patch(
                "app.services.folder_list.ORMRepository",
                return_value=repository,
            ),
            patch(
                "app.services.folder_list.hooks.emit",
                new=AsyncMock(),
            ) as emit_mock,
        ):
            result_folders, result_count, result_recursive = (
                await list_folders(session, params)
            )

        repository.select.assert_awaited_once_with(Folder, obj_id=42)
        repository.select_parent_chain.assert_awaited_once_with(parent)
        parent.is_write_protected_recursive.assert_called_once_with(
            parent_chain,
        )
        repository.count_all.assert_awaited_once_with(
            Folder,
            order_by="created_at",
            order="desc",
            parent_id__eq=42,
        )
        repository.select_all.assert_awaited_once_with(
            Folder,
            order_by="created_at",
            order="desc",
            parent_id__eq=42,
        )
        emit_mock.assert_awaited_once_with(
            E.FOLDER_LIST_COMPLETED,
            session,
            folders,
        )

        self.assertEqual(result_folders, folders)
        self.assertEqual(result_count, 1)
        self.assertTrue(result_recursive)

    async def test_lists_child_folders_recursive_true_parent_itself_protected(
        self,
    ):
        session = AsyncMock()
        params = FolderListRequest(parent_id__eq=42)

        parent = MagicMock(spec=Folder)
        parent.is_write_protected = True
        parent.is_write_protected_recursive.return_value = False
        parent_chain = []
        folders = [MagicMock(spec=Folder)]

        repository = AsyncMock()
        repository.select.return_value = parent
        repository.select_parent_chain.return_value = parent_chain
        repository.count_all.return_value = 1
        repository.select_all.return_value = folders

        with (
            patch(
                "app.services.folder_list.ORMRepository",
                return_value=repository,
            ),
            patch(
                "app.services.folder_list.hooks.emit",
                new=AsyncMock(),
            ),
        ):
            _, _, result_recursive = await list_folders(session, params)

        self.assertTrue(result_recursive)

    async def test_raises_not_found_when_parent_does_not_exist(self):
        session = AsyncMock()
        params = FolderListRequest(
            order_by="dirname",
            order="asc",
            parent_id__eq=42,
        )

        repository = AsyncMock()
        repository.select.return_value = None

        with (
            patch(
                "app.services.folder_list.ORMRepository",
                return_value=repository,
            ),
            patch(
                "app.services.folder_list.hooks.emit",
                new=AsyncMock(),
            ) as emit_mock,
        ):
            with self.assertRaises(ResourceNotFoundError):
                await list_folders(session, params)

        repository.select.assert_awaited_once_with(Folder, obj_id=42)
        repository.select_parent_chain.assert_not_awaited()
        repository.count_all.assert_not_awaited()
        repository.select_all.assert_not_awaited()
        emit_mock.assert_not_awaited()

    async def test_root_list_passes_default_order_and_null_parent_filter(
        self,
    ):
        session = AsyncMock()
        params = FolderListRequest()

        repository = AsyncMock()
        repository.count_all.return_value = 0
        repository.select_all.return_value = []

        with (
            patch(
                "app.services.folder_list.ORMRepository",
                return_value=repository,
            ),
            patch(
                "app.services.folder_list.hooks.emit",
                new=AsyncMock(),
            ),
        ):
            result_folders, result_count, result_recursive = (
                await list_folders(session, params)
            )

        repository.count_all.assert_awaited_once_with(
            Folder,
            order_by="dirname",
            order="asc",
            parent_id__is=None,
        )
        repository.select_all.assert_awaited_once_with(
            Folder,
            order_by="dirname",
            order="asc",
            parent_id__is=None,
        )
        self.assertEqual(result_folders, [])
        self.assertEqual(result_count, 0)
        self.assertFalse(result_recursive)
