# tests/services/test_file_list.py
# SPDX-License-Identifier: SSPL-1.0

import unittest
from unittest.mock import AsyncMock, MagicMock, patch

from app.errors import ResourceNotFoundError
from app.events import Events as E
from app.models.file import File
from app.models.file_tag import FileTag
from app.models.folder import Folder
from app.schemas.file_list import FileListRequest
from app.services.file_list import list_files


class TestListFiles(unittest.IsolatedAsyncioTestCase):

    async def test_lists_files_and_emits_hook(self):
        session = AsyncMock()
        params = FileListRequest(
            folder_id__eq=42,
            order_by="filename",
            order="asc",
        )

        folder = MagicMock(spec=Folder)
        files = [MagicMock(spec=File), MagicMock(spec=File)]

        repository = AsyncMock()
        repository.select.return_value = folder
        repository.count_all.return_value = 2
        repository.select_all.return_value = files

        with (
            patch(
                "app.services.file_list.ORMRepository",
                return_value=repository,
            ),
            patch(
                "app.services.file_list.hooks.emit",
                new=AsyncMock(),
            ) as emit_mock,
        ):
            result_files, result_count = await list_files(
                session,
                params,
            )

        repository.select.assert_awaited_once_with(Folder, obj_id=42)
        repository.count_all.assert_awaited_once_with(
            File,
            offset=0,
            limit=50,
            order_by="filename",
            order="asc",
            folder_id=42,
        )
        repository.select_all.assert_awaited_once_with(
            File,
            offset=0,
            limit=50,
            order_by="filename",
            order="asc",
            folder_id=42,
        )
        emit_mock.assert_awaited_once_with(
            E.FILE_LIST_COMPLETED,
            session,
            files,
        )

        self.assertEqual(result_files, files)
        self.assertEqual(result_count, 2)

    async def test_raises_not_found_when_folder_does_not_exist(self):
        session = AsyncMock()
        params = FileListRequest(
            folder_id__eq=42,
            order_by="filename",
            order="asc",
        )

        repository = AsyncMock()
        repository.select.return_value = None

        with (
            patch(
                "app.services.file_list.ORMRepository",
                return_value=repository,
            ),
            patch(
                "app.services.file_list.hooks.emit",
                new=AsyncMock(),
            ) as emit_mock,
        ):
            with self.assertRaises(ResourceNotFoundError):
                await list_files(session, params)

        repository.select.assert_awaited_once_with(Folder, obj_id=42)
        repository.count_all.assert_not_awaited()
        repository.select_all.assert_not_awaited()
        emit_mock.assert_not_awaited()

    async def test_global_list_skips_folder_select_and_folder_filter(
        self,
    ):
        session = AsyncMock()
        params = FileListRequest(order_by="filename", order="asc")

        files = [MagicMock(spec=File)]

        repository = AsyncMock()
        repository.count_all.return_value = 1
        repository.select_all.return_value = files

        with (
            patch(
                "app.services.file_list.ORMRepository",
                return_value=repository,
            ),
            patch(
                "app.services.file_list.hooks.emit",
                new=AsyncMock(),
            ) as emit_mock,
        ):
            result_files, result_count = await list_files(
                session,
                params,
            )

        repository.select.assert_not_awaited()
        repository.count_all.assert_awaited_once_with(
            File,
            offset=0,
            limit=50,
            order_by="filename",
            order="asc",
        )
        repository.select_all.assert_awaited_once_with(
            File,
            offset=0,
            limit=50,
            order_by="filename",
            order="asc",
        )
        emit_mock.assert_awaited_once_with(
            E.FILE_LIST_COMPLETED,
            session,
            files,
        )

        self.assertEqual(result_files, files)
        self.assertEqual(result_count, 1)

    async def test_passes_default_order_and_folder_filter(self):
        session = AsyncMock()
        params = FileListRequest(folder_id__eq=42)

        folder = MagicMock(spec=Folder)

        repository = AsyncMock()
        repository.select.return_value = folder
        repository.count_all.return_value = 0
        repository.select_all.return_value = []

        with (
            patch(
                "app.services.file_list.ORMRepository",
                return_value=repository,
            ),
            patch(
                "app.services.file_list.hooks.emit",
                new=AsyncMock(),
            ),
        ):
            result_files, result_count = await list_files(
                session,
                params,
            )

        repository.select.assert_awaited_once_with(Folder, obj_id=42)
        repository.count_all.assert_awaited_once_with(
            File,
            offset=0,
            limit=50,
            order_by="filename",
            order="asc",
            folder_id=42,
        )
        repository.select_all.assert_awaited_once_with(
            File,
            offset=0,
            limit=50,
            order_by="filename",
            order="asc",
            folder_id=42,
        )

        self.assertEqual(result_files, [])
        self.assertEqual(result_count, 0)

    async def test_wraps_filename_ilike_filter(self):
        session = AsyncMock()
        params = FileListRequest(
            folder_id__eq=42,
            filename__ilike="report",
            order_by="filename",
            order="asc",
        )

        folder = MagicMock(spec=Folder)
        files = [MagicMock(spec=File)]

        repository = AsyncMock()
        repository.select.return_value = folder
        repository.count_all.return_value = 1
        repository.select_all.return_value = files

        with (
            patch(
                "app.services.file_list.ORMRepository",
                return_value=repository,
            ),
            patch(
                "app.services.file_list.hooks.emit",
                new=AsyncMock(),
            ),
        ):
            result_files, result_count = await list_files(
                session,
                params,
            )

        repository.count_all.assert_awaited_once_with(
            File,
            filename__ilike="%report%",
            offset=0,
            limit=50,
            order_by="filename",
            order="asc",
            folder_id=42,
        )
        repository.select_all.assert_awaited_once_with(
            File,
            filename__ilike="%report%",
            offset=0,
            limit=50,
            order_by="filename",
            order="asc",
            folder_id=42,
        )

        self.assertEqual(result_files, files)
        self.assertEqual(result_count, 1)

    async def test_wraps_mimetype_ilike_filter(self):
        session = AsyncMock()
        params = FileListRequest(
            folder_id__eq=42,
            mimetype__ilike="image",
            order_by="mimetype",
            order="desc",
        )

        folder = MagicMock(spec=Folder)
        files = [MagicMock(spec=File)]

        repository = AsyncMock()
        repository.select.return_value = folder
        repository.count_all.return_value = 1
        repository.select_all.return_value = files

        with (
            patch(
                "app.services.file_list.ORMRepository",
                return_value=repository,
            ),
            patch(
                "app.services.file_list.hooks.emit",
                new=AsyncMock(),
            ),
        ):
            result_files, result_count = await list_files(
                session,
                params,
            )

        repository.count_all.assert_awaited_once_with(
            File,
            mimetype__ilike="%image%",
            offset=0,
            limit=50,
            order_by="mimetype",
            order="desc",
            folder_id=42,
        )
        repository.select_all.assert_awaited_once_with(
            File,
            mimetype__ilike="%image%",
            offset=0,
            limit=50,
            order_by="mimetype",
            order="desc",
            folder_id=42,
        )

        self.assertEqual(result_files, files)
        self.assertEqual(result_count, 1)

    async def test_filters_by_tag_eq_using_subquery(self):
        session = AsyncMock()
        params = FileListRequest(
            folder_id__eq=42,
            tag__eq="report",
            order_by="filename",
            order="asc",
        )

        folder = MagicMock(spec=Folder)
        files = [MagicMock(spec=File)]
        fake_subquery = MagicMock()

        repository = AsyncMock()
        repository.select.return_value = folder
        repository.count_all.return_value = 1
        repository.select_all.return_value = files
        repository.make_subquery = MagicMock(return_value=fake_subquery)

        with (
            patch(
                "app.services.file_list.ORMRepository",
                return_value=repository,
            ),
            patch(
                "app.services.file_list.hooks.emit",
                new=AsyncMock(),
            ),
        ):
            result_files, result_count = await list_files(
                session,
                params,
            )

        repository.make_subquery.assert_called_once_with(
            FileTag,
            "file_id",
            tag__eq="report",
        )

        expected_filters = {
            "offset": 0,
            "limit": 50,
            "order_by": "filename",
            "order": "asc",
            "folder_id": 42,
            "id__subquery": fake_subquery,
        }

        repository.count_all.assert_awaited_once_with(
            File,
            **expected_filters,
        )
        repository.select_all.assert_awaited_once_with(
            File,
            **expected_filters,
        )

        self.assertEqual(result_files, files)
        self.assertEqual(result_count, 1)

    async def test_tag_eq_passes_value_unchanged(self):
        session = AsyncMock()
        params = FileListRequest(tag__eq="  hello  ")

        files = []
        fake_subquery = MagicMock()

        repository = AsyncMock()
        repository.count_all.return_value = 0
        repository.select_all.return_value = files
        repository.make_subquery = MagicMock(return_value=fake_subquery)

        with (
            patch(
                "app.services.file_list.ORMRepository",
                return_value=repository,
            ),
            patch(
                "app.services.file_list.hooks.emit",
                new=AsyncMock(),
            ),
        ):
            await list_files(session, params)

        repository.make_subquery.assert_called_once_with(
            FileTag,
            "file_id",
            tag__eq="hello",
        )

    async def test_tag_eq_absent_does_not_call_make_subquery(self):
        session = AsyncMock()
        params = FileListRequest()

        repository = AsyncMock()
        repository.count_all.return_value = 0
        repository.select_all.return_value = []

        with (
            patch(
                "app.services.file_list.ORMRepository",
                return_value=repository,
            ),
            patch(
                "app.services.file_list.hooks.emit",
                new=AsyncMock(),
            ),
        ):
            await list_files(session, params)

        repository.make_subquery.assert_not_called()

        call_kwargs = repository.count_all.call_args.kwargs
        self.assertNotIn("id__subquery", call_kwargs)

    async def test_passes_all_filters_to_repository(self):
        session = AsyncMock()
        params = FileListRequest(
            folder_id__eq=42,
            created_at__ge=100,
            created_at__le=200,
            updated_at__ge=300,
            updated_at__le=400,
            is_starred__eq=True,
            filename__ilike="report",
            mimetype__ilike="pdf",
            tag__eq="draft",
            offset=10,
            limit=20,
            order_by="created_at",
            order="desc",
        )

        folder = MagicMock(spec=Folder)
        files = [MagicMock(spec=File)]
        fake_subquery = MagicMock()

        repository = AsyncMock()
        repository.select.return_value = folder
        repository.count_all.return_value = 1
        repository.select_all.return_value = files
        repository.make_subquery = MagicMock(return_value=fake_subquery)

        with (
            patch(
                "app.services.file_list.ORMRepository",
                return_value=repository,
            ),
            patch(
                "app.services.file_list.hooks.emit",
                new=AsyncMock(),
            ),
        ):
            result_files, result_count = await list_files(
                session,
                params,
            )

        repository.make_subquery.assert_called_once_with(
            FileTag,
            "file_id",
            tag__eq="draft",
        )

        expected_filters = {
            "created_at__ge": 100,
            "created_at__le": 200,
            "updated_at__ge": 300,
            "updated_at__le": 400,
            "is_starred__eq": True,
            "filename__ilike": "%report%",
            "mimetype__ilike": "%pdf%",
            "offset": 10,
            "limit": 20,
            "order_by": "created_at",
            "order": "desc",
            "folder_id": 42,
            "id__subquery": fake_subquery,
        }

        repository.count_all.assert_awaited_once_with(
            File,
            **expected_filters,
        )
        repository.select_all.assert_awaited_once_with(
            File,
            **expected_filters,
        )

        self.assertEqual(result_files, files)
        self.assertEqual(result_count, 1)
