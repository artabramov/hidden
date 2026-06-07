# tests/routers/test_file_select.py
# SPDX-License-Identifier: SSPL-1.0

import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

from app.models.user import User


from tests.helpers import set_minimal_app_config_env


set_minimal_app_config_env()

from app.models.file import FileType  # noqa: E402
from app.routers.file_select import file_select_router  # noqa: E402
from app.schemas.file_select import FileSelectResponse  # noqa: E402


class TestFileSelectRouter(unittest.IsolatedAsyncioTestCase):

    async def test_returns_file(self):
        session = AsyncMock()
        current_user = MagicMock(spec=User)

        file = SimpleNamespace(
            id=42,
            folder_id=7,
            file_created_by_user=SimpleNamespace(
                id=1,
                display_name="Uploader",
            ),
            created_at=100,
            file_updated_by_user=SimpleNamespace(
                id=2,
                display_name="Updater",
            ),
            updated_at=200,
            is_starred=True,
            filename="document.txt",
            filesize=1024,
            mimetype="text/plain",
            checksum="a" * 64,
            summary="File summary.",
            comments_count=1,
            latest_revision_number=1,
            file_tags=[
                SimpleNamespace(tag="docs"),
                SimpleNamespace(tag="text"),
            ],
            file_thumbnail=SimpleNamespace(id=9),
            file_comments=[
                SimpleNamespace(
                    id=3,
                    comment_created_by_user=SimpleNamespace(
                        id=4,
                        display_name="Comment Author",
                    ),
                    created_at=300,
                    updated_at=None,
                    body="Comment body.",
                ),
            ],
            file_revisions=[
                SimpleNamespace(
                    id=5,
                    revision_number=1,
                    revision_created_by_user=SimpleNamespace(
                        id=6,
                        display_name="Revision Author",
                    ),
                    created_at=400,
                    filesize=1024,
                    mimetype="text/plain",
                    checksum="b" * 64,
                ),
            ],
        )

        file.has_thumbnail = True
        file.filetype = FileType.TEXT

        with patch(
            "app.routers.file_select.select_file",
            new_callable=AsyncMock,
            return_value=file,
        ) as mock_service:
            out = await file_select_router(
                file_id=42,
                session=session,
                current_user=current_user,
            )

        mock_service.assert_awaited_once_with(
            session=session,
            file_id=42,
        )

        self.assertIsInstance(out, FileSelectResponse)
        self.assertEqual(out.file_id, 42)
        self.assertEqual(out.folder_id, 7)
        self.assertEqual(out.created_by.user_id, 1)
        self.assertEqual(out.created_by.display_name, "Uploader")
        self.assertEqual(out.updated_by.user_id, 2)
        self.assertEqual(out.updated_by.display_name, "Updater")
        self.assertEqual(out.created_at, 100)
        self.assertEqual(out.updated_at, 200)
        self.assertTrue(out.is_starred)
        self.assertEqual(out.filename, "document.txt")
        self.assertEqual(out.filesize, 1024)
        self.assertEqual(out.mimetype, "text/plain")
        self.assertEqual(out.checksum, "a" * 64)
        self.assertEqual(out.summary, "File summary.")
        self.assertEqual(out.comments_count, 1)
        self.assertEqual(out.latest_revision_number, 1)
        self.assertEqual(out.file_tags, ["docs", "text"])
        self.assertTrue(out.has_thumbnail)
        self.assertEqual(out.filetype, FileType.TEXT)
        self.assertEqual(out.file_comments[0].comment_id, 3)
        self.assertEqual(
            out.file_comments[0].created_by.display_name,
            "Comment Author",
        )
        self.assertEqual(out.file_revisions[0].revision_id, 5)
        self.assertEqual(
            out.file_revisions[0].created_by.display_name,
            "Revision Author",
        )

    async def test_returns_file_with_nullable_fields(self):
        session = AsyncMock()
        current_user = MagicMock(spec=User)

        file = SimpleNamespace(
            id=43,
            folder_id=7,
            file_created_by_user=SimpleNamespace(
                id=1,
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
            file_thumbnail=None,
            file_comments=[],
            file_revisions=[],
        )

        file.has_thumbnail = False
        file.filetype = FileType.BINARY

        with patch(
            "app.routers.file_select.select_file",
            new_callable=AsyncMock,
            return_value=file,
        ) as mock_service:
            out = await file_select_router(
                file_id=43,
                session=session,
                current_user=current_user,
            )

        mock_service.assert_awaited_once_with(
            session=session,
            file_id=43,
        )

        self.assertEqual(out.file_id, 43)
        self.assertIsNone(out.updated_by)
        self.assertIsNone(out.updated_at)
        self.assertIsNone(out.mimetype)
        self.assertIsNone(out.summary)
        self.assertEqual(out.file_tags, [])
        self.assertFalse(out.has_thumbnail)
        self.assertEqual(out.filetype, FileType.BINARY)
        self.assertEqual(out.file_comments, [])
        self.assertEqual(out.file_revisions, [])
