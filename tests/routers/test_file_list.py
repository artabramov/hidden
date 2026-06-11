# tests/routers/test_file_list.py
# SPDX-License-Identifier: GPL-3.0-only

import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from app.models.file import FileType
from app.schemas.file_list import FileListRequest

from tests.helpers import set_minimal_app_config_env


set_minimal_app_config_env()

from app.routers.file_list import file_list_router  # noqa: E402


class TestFileListRouter(unittest.IsolatedAsyncioTestCase):

    async def test_returns_file_list_response(self):
        session = AsyncMock()
        current_user = SimpleNamespace(id=1)
        params = FileListRequest(folder_id__eq=2)

        files = [
            SimpleNamespace(
                id=1,
                folder_id=2,
                file_created_by_user=SimpleNamespace(
                    id=3,
                    display_name="Uploader",
                ),
                created_at=100,
                file_updated_by_user=None,
                updated_at=None,
                is_starred=False,
                filename="document.txt",
                filesize=1024,
                mimetype="text/plain",
                checksum="a" * 64,
                summary=None,
                comments_count=0,
                latest_revision_number=1,
                file_tags=[
                    SimpleNamespace(tag="docs"),
                    SimpleNamespace(tag="text"),
                ],
                has_thumbnail=False,
                filetype=FileType.TEXT,
            ),
        ]

        with patch(
            "app.routers.file_list.list_files",
            new=AsyncMock(return_value=(files, 1)),
        ) as list_files_mock:
            response = await file_list_router(
                session=session,
                params=params,
                current_user=current_user,
            )

        list_files_mock.assert_awaited_once_with(
            session=session,
            params=params,
        )

        self.assertEqual(response.files_count, 1)
        self.assertEqual(len(response.files), 1)
        self.assertEqual(response.files[0].filetype, FileType.TEXT)
        self.assertEqual(response.files[0].file_id, 1)
        self.assertEqual(response.files[0].folder_id, 2)
        self.assertEqual(response.files[0].created_by.user_id, 3)
        self.assertEqual(response.files[0].created_by.display_name, "Uploader")
        self.assertIsNone(response.files[0].updated_by)
        self.assertIsNone(response.files[0].updated_at)
        self.assertEqual(response.files[0].filename, "document.txt")
        self.assertEqual(response.files[0].file_tags, ["docs", "text"])
        self.assertFalse(response.files[0].has_thumbnail)

    async def test_returns_global_file_list_response(self):
        session = AsyncMock()
        current_user = SimpleNamespace(id=1)
        params = FileListRequest(filename__ilike="doc")

        files = [
            SimpleNamespace(
                id=1,
                folder_id=9,
                file_created_by_user=SimpleNamespace(
                    id=3,
                    display_name="Uploader",
                ),
                created_at=100,
                file_updated_by_user=None,
                updated_at=None,
                is_starred=False,
                filename="document.txt",
                filesize=1024,
                mimetype="text/plain",
                checksum="a" * 64,
                summary=None,
                comments_count=0,
                latest_revision_number=1,
                file_tags=[],
                has_thumbnail=False,
                filetype=FileType.TEXT,
            ),
        ]

        with patch(
            "app.routers.file_list.list_files",
            new=AsyncMock(return_value=(files, 1)),
        ) as list_files_mock:
            response = await file_list_router(
                session=session,
                params=params,
                current_user=current_user,
            )

        list_files_mock.assert_awaited_once_with(
            session=session,
            params=params,
        )

        self.assertEqual(response.files_count, 1)
        self.assertEqual(response.files[0].folder_id, 9)

    async def test_returns_empty_file_list_response(self):
        session = AsyncMock()
        current_user = SimpleNamespace(id=1)
        params = FileListRequest(folder_id__eq=2)

        with patch(
            "app.routers.file_list.list_files",
            new=AsyncMock(return_value=([], 0)),
        ) as list_files_mock:
            response = await file_list_router(
                session=session,
                params=params,
                current_user=current_user,
            )

        list_files_mock.assert_awaited_once_with(
            session=session,
            params=params,
        )

        self.assertEqual(response.files, [])
        self.assertEqual(response.files_count, 0)

    async def test_returns_file_with_nullable_fields(self):
        session = AsyncMock()
        current_user = SimpleNamespace(id=1)
        params = FileListRequest(folder_id__eq=2)

        files = [
            SimpleNamespace(
                id=1,
                folder_id=2,
                file_created_by_user=SimpleNamespace(
                    id=3,
                    display_name="Uploader",
                ),
                created_at=100,
                file_updated_by_user=None,
                updated_at=None,
                is_starred=False,
                filename="document.txt",
                filesize=1024,
                mimetype=None,
                checksum="a" * 64,
                summary=None,
                comments_count=0,
                latest_revision_number=0,
                file_tags=[],
                has_thumbnail=False,
                filetype=FileType.BINARY,
            ),
        ]

        with patch(
            "app.routers.file_list.list_files",
            new=AsyncMock(return_value=(files, 1)),
        ) as list_files_mock:
            response = await file_list_router(
                session=session,
                params=params,
                current_user=current_user,
            )

        list_files_mock.assert_awaited_once_with(
            session=session,
            params=params,
        )

        self.assertEqual(response.files_count, 1)
        self.assertEqual(len(response.files), 1)
        self.assertEqual(response.files[0].filetype, FileType.BINARY)
        self.assertIsNone(response.files[0].updated_by)
        self.assertIsNone(response.files[0].updated_at)
        self.assertIsNone(response.files[0].mimetype)
        self.assertIsNone(response.files[0].summary)
        self.assertEqual(response.files[0].file_tags, [])
        self.assertFalse(response.files[0].has_thumbnail)
