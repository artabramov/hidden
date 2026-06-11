# tests/services/test_file_download.py
# SPDX-License-Identifier: GPL-3.0-only

import unittest
from unittest.mock import AsyncMock, MagicMock, call, patch

from app.errors import ResourceNotFoundError
from app.events import Events as E
from app.models.file import File
from app.models.file_revision import FileRevision
from app.services.file_download import download_file


class TestDownloadFile(unittest.IsolatedAsyncioTestCase):

    def _build_file(self):
        folder = MagicMock()
        parent_chain = (MagicMock(),)

        file = MagicMock(spec=File)
        file.id = 42
        file.filename = "document.txt"
        file.mimetype = "text/plain"
        file.file_folder = folder
        file.get_absolute_path.return_value = "/mnt/files/document.txt"

        return file, folder, parent_chain

    def _build_revision(self):
        revision = MagicMock(spec=FileRevision)
        revision.filename = "document.txt"
        revision.mimetype = "text/plain"
        revision.absolute_path = "/mnt/revisions/some-uuid"
        return revision

    # --- revision_number=0 (HEAD) ---

    async def test_head_returns_file_and_path_and_emits_hook(self):
        session = AsyncMock()
        file, folder, parent_chain = self._build_file()

        repository = AsyncMock()
        repository.select.return_value = file
        repository.select_parent_chain.return_value = parent_chain

        with (
            patch(
                "app.services.file_download.ORMRepository",
                return_value=repository,
            ),
            patch(
                "app.services.file_download.isfile",
                new=AsyncMock(return_value=True),
            ) as isfile_mock,
            patch(
                "app.services.file_download.write_audit",
                new=AsyncMock(),
            ) as audit_mock,
            patch(
                "app.services.file_download.hooks.emit",
                new=AsyncMock(),
            ) as emit_mock,
        ):
            result, result_path = await download_file(session, 42, 0)

        repository.select.assert_awaited_once_with(File, obj_id=42)
        repository.select_parent_chain.assert_awaited_once_with(folder)
        file.get_absolute_path.assert_called_once_with(folder, parent_chain)
        isfile_mock.assert_awaited_once_with("/mnt/files/document.txt")

        audit_mock.assert_awaited_once_with(
            repository=repository,
            event=E.FILE_DOWNLOAD_COMPLETED,
            resource_type=File.__tablename__,
            resource_id=42,
        )
        repository.commit.assert_awaited_once_with()
        emit_mock.assert_awaited_once_with(
            E.FILE_DOWNLOAD_COMPLETED, session, file
        )

        self.assertIs(result, file)
        self.assertEqual(result_path, "/mnt/files/document.txt")

    async def test_head_raises_not_found_when_file_missing_on_disk(self):
        session = AsyncMock()
        file, folder, parent_chain = self._build_file()

        repository = AsyncMock()
        repository.select.return_value = file
        repository.select_parent_chain.return_value = parent_chain

        with (
            patch(
                "app.services.file_download.ORMRepository",
                return_value=repository,
            ),
            patch(
                "app.services.file_download.isfile",
                new=AsyncMock(return_value=False),
            ) as isfile_mock,
            patch(
                "app.services.file_download.hooks.emit",
                new=AsyncMock(),
            ) as emit_mock,
        ):
            with self.assertRaises(ResourceNotFoundError):
                await download_file(session, 42, 0)

        isfile_mock.assert_awaited_once_with("/mnt/files/document.txt")
        emit_mock.assert_not_awaited()

    # --- revision_number>=1 (historical) ---

    async def test_historical_returns_revision_and_path_and_emits_hook(self):
        session = AsyncMock()
        file, _, _ = self._build_file()
        revision = self._build_revision()

        repository = AsyncMock()
        repository.select.side_effect = [file, revision]

        with (
            patch(
                "app.services.file_download.ORMRepository",
                return_value=repository,
            ),
            patch(
                "app.services.file_download.isfile",
                new=AsyncMock(return_value=True),
            ) as isfile_mock,
            patch(
                "app.services.file_download.write_audit",
                new=AsyncMock(),
            ) as audit_mock,
            patch(
                "app.services.file_download.hooks.emit",
                new=AsyncMock(),
            ) as emit_mock,
        ):
            result, result_path = await download_file(session, 42, 3)

        self.assertEqual(
            repository.select.await_args_list,
            [
                call(File, obj_id=42),
                call(FileRevision, file_id=42, revision_number=3),
            ],
        )
        repository.select_parent_chain.assert_not_called()
        isfile_mock.assert_awaited_once_with("/mnt/revisions/some-uuid")

        audit_mock.assert_awaited_once_with(
            repository=repository,
            event=E.FILE_DOWNLOAD_COMPLETED,
            resource_type=File.__tablename__,
            resource_id=42,
        )
        repository.commit.assert_awaited_once_with()
        emit_mock.assert_awaited_once_with(
            E.FILE_DOWNLOAD_COMPLETED, session, file
        )

        self.assertIs(result, revision)
        self.assertEqual(result_path, "/mnt/revisions/some-uuid")

    async def test_historical_raises_not_found_when_revision_not_exists(self):
        session = AsyncMock()
        file, _, _ = self._build_file()

        repository = AsyncMock()
        repository.select.side_effect = [file, None]

        with (
            patch(
                "app.services.file_download.ORMRepository",
                return_value=repository,
            ),
            patch(
                "app.services.file_download.isfile",
                new=AsyncMock(),
            ) as isfile_mock,
            patch(
                "app.services.file_download.hooks.emit",
                new=AsyncMock(),
            ) as emit_mock,
        ):
            with self.assertRaises(ResourceNotFoundError):
                await download_file(session, 42, 3)

        self.assertEqual(
            repository.select.await_args_list,
            [
                call(File, obj_id=42),
                call(FileRevision, file_id=42, revision_number=3),
            ],
        )
        isfile_mock.assert_not_awaited()
        emit_mock.assert_not_awaited()

    async def test_historical_raises_not_found_when_file_missing_on_disk(self):
        session = AsyncMock()
        file, _, _ = self._build_file()
        revision = self._build_revision()

        repository = AsyncMock()
        repository.select.side_effect = [file, revision]

        with (
            patch(
                "app.services.file_download.ORMRepository",
                return_value=repository,
            ),
            patch(
                "app.services.file_download.isfile",
                new=AsyncMock(return_value=False),
            ) as isfile_mock,
            patch(
                "app.services.file_download.hooks.emit",
                new=AsyncMock(),
            ) as emit_mock,
        ):
            with self.assertRaises(ResourceNotFoundError):
                await download_file(session, 42, 3)

        isfile_mock.assert_awaited_once_with("/mnt/revisions/some-uuid")
        emit_mock.assert_not_awaited()

    # --- common ---

    async def test_raises_not_found_when_file_does_not_exist(self):
        session = AsyncMock()

        repository = AsyncMock()
        repository.select.return_value = None

        with (
            patch(
                "app.services.file_download.ORMRepository",
                return_value=repository,
            ),
            patch(
                "app.services.file_download.isfile",
                new=AsyncMock(),
            ) as isfile_mock,
            patch(
                "app.services.file_download.hooks.emit",
                new=AsyncMock(),
            ) as emit_mock,
        ):
            with self.assertRaises(ResourceNotFoundError):
                await download_file(session, 42, 0)

        repository.select.assert_awaited_once_with(File, obj_id=42)
        isfile_mock.assert_not_awaited()
        emit_mock.assert_not_awaited()
