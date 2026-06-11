# tests/services/test_file_upload.py
# SPDX-License-Identifier: GPL-3.0-only

import unittest
import uuid
from contextlib import ExitStack
from unittest.mock import AsyncMock, MagicMock, patch

from sqlalchemy.exc import IntegrityError

from app.db.engine import load_all_models
from app.errors import (
    ResourceConflictError,
    ResourceLockedError,
    ResourceNotFoundError,
    ValueInvalidError,
)
from app.events import Events as E
from app.locks import LockType
from app.models.file import File
from app.models.file_revision import FileRevision
from app.models.file_thumbnail import FileThumbnail
from app.models.folder import Folder
from app.models.user import User
from app.services.file_upload import _cleanup_path, upload_file

load_all_models()

# Staging path returned by patched get_tmp_path (no real temp I/O).
STAGED_TMP = "/mnt/files/__staged_upload__"


class TestUploadFile(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        super().setUp()
        self.thumbnail_cache_mock = MagicMock()
        self._thumbnail_cache_patcher = patch(
            "app.services.file_upload.get_thumbnail_cache",
            return_value=self.thumbnail_cache_mock,
        )
        self._thumbnail_cache_patcher.start()
        self.addCleanup(self._thumbnail_cache_patcher.stop)

    def _build_user(self):
        user = MagicMock(spec=User)
        user.id = 10
        return user

    def _build_upload(self, filename="document.txt"):
        uploaded = AsyncMock()
        uploaded.filename = filename
        return uploaded

    def _build_lock_context(self):
        lock_context = AsyncMock()
        lock_context.__aenter__.return_value = None
        lock_context.__aexit__.return_value = None
        return lock_context

    def _build_folder(self):
        folder = Folder(
            parent_id=None,
            folder_parent=None,
            created_by=10,
            dirname="documents",
            summary=None,
            children_count=0,
            files_count=0,
        )
        folder.id = 1
        folder.is_write_protected = False
        return folder

    def _build_existing_file_mock(self):
        existing = MagicMock(spec=File)
        existing.id = 42
        existing.filename = "document.txt"
        existing.folder_id = 1
        existing.filesize = 50
        existing.mimetype = "text/plain"
        existing.checksum = "b" * 64
        existing.updated_by = None
        existing.file_thumbnail = None
        existing.latest_revision_number = 0
        return existing

    async def test_raises_not_found_when_folder_missing(self):
        session = AsyncMock()
        user = self._build_user()
        uploaded = self._build_upload()

        repository = AsyncMock()
        repository.select.return_value = None

        with (
            patch(
                "app.services.file_upload.ORMRepository",
                return_value=repository,
            ),
            patch(
                "app.services.file_upload.locks.lock_directory",
            ) as lock_directory_mock,
            patch(
                "app.services.file_upload.upload", new=AsyncMock()
            ) as upload_mock,
            patch(
                "app.services.file_upload.delete", new=AsyncMock()
            ) as delete_mock,
            patch(
                "app.services.file_upload.write_audit", new=AsyncMock()
                ) as write_audit_mock,
            patch(
                "app.services.file_upload.hooks.emit", new=AsyncMock()
            ) as emit_mock,
            patch(
                "app.services.file_upload.isdir",
                new=AsyncMock(return_value=False),
            ),
            patch(
                "app.services.file_upload.isfile",
                new=AsyncMock(return_value=False),
            ),
        ):
            with self.assertRaises(ResourceNotFoundError):
                await upload_file(session, user, 1, uploaded)

        repository.select.assert_awaited_once_with(Folder, obj_id=1)
        repository.select_parent_chain.assert_not_awaited()
        repository.insert.assert_not_awaited()
        repository.update.assert_not_awaited()
        repository.rollback.assert_not_awaited()
        repository.commit.assert_not_awaited()

        lock_directory_mock.assert_not_called()
        upload_mock.assert_not_awaited()
        delete_mock.assert_not_awaited()
        write_audit_mock.assert_not_awaited()
        emit_mock.assert_not_awaited()

    async def test_raises_locked_when_folder_write_protected(self):
        session = AsyncMock()
        user = self._build_user()
        uploaded = self._build_upload()

        folder = self._build_folder()
        folder.is_write_protected = True

        repository = AsyncMock()
        repository.select.return_value = folder
        repository.select_parent_chain.return_value = ()

        with (
            patch(
                "app.services.file_upload.ORMRepository",
                return_value=repository,
            ),
            patch(
                "app.services.file_upload.locks.lock_directory",
            ) as lock_directory_mock,
            patch(
                "app.services.file_upload.upload", new=AsyncMock()
            ) as upload_mock,
            patch(
                "app.services.file_upload.delete", new=AsyncMock()
            ) as delete_mock,
            patch(
                "app.services.file_upload.write_audit", new=AsyncMock()
            ) as write_audit_mock,
            patch(
                "app.services.file_upload.hooks.emit", new=AsyncMock()
            ) as emit_mock,
            patch(
                "app.services.file_upload.isdir",
                new=AsyncMock(return_value=False),
            ),
            patch(
                "app.services.file_upload.isfile",
                new=AsyncMock(return_value=False),
            ),
        ):
            with self.assertRaises(ResourceLockedError):
                await upload_file(session, user, 1, uploaded)

        repository.select.assert_awaited_once_with(Folder, obj_id=1)
        repository.select_parent_chain.assert_awaited_once_with(folder)
        repository.insert.assert_not_awaited()
        repository.update.assert_not_awaited()
        repository.rollback.assert_not_awaited()
        repository.commit.assert_not_awaited()

        lock_directory_mock.assert_not_called()
        upload_mock.assert_not_awaited()
        delete_mock.assert_not_awaited()
        write_audit_mock.assert_not_awaited()
        emit_mock.assert_not_awaited()

    async def test_raises_invalid_when_filename_invalid(self):
        session = AsyncMock()
        user = self._build_user()
        uploaded = self._build_upload("../bad.txt")

        folder = self._build_folder()

        repository = AsyncMock()
        repository.select.return_value = folder
        repository.select_parent_chain.return_value = ()

        with (
            patch(
                "app.services.file_upload.ORMRepository",
                return_value=repository,
            ),
            patch(
                "app.services.file_upload.locks.lock_directory",
            ) as lock_directory_mock,
            patch(
                "app.services.file_upload.upload", new=AsyncMock()
            ) as upload_mock,
            patch(
                "app.services.file_upload.delete", new=AsyncMock()
            ) as delete_mock,
            patch(
                "app.services.file_upload.write_audit", new=AsyncMock()
            ) as write_audit_mock,
            patch(
                "app.services.file_upload.hooks.emit", new=AsyncMock()
            ) as emit_mock,
            patch(
                "app.services.file_upload.isdir",
                new=AsyncMock(return_value=False),
            ),
            patch(
                "app.services.file_upload.isfile",
                new=AsyncMock(return_value=False),
            ),
        ):
            with self.assertRaises(ValueInvalidError):
                await upload_file(session, user, 1, uploaded)

        repository.select.assert_awaited_once_with(Folder, obj_id=1)
        repository.select_parent_chain.assert_awaited_once_with(folder)
        repository.insert.assert_not_awaited()
        repository.update.assert_not_awaited()
        repository.rollback.assert_not_awaited()
        repository.commit.assert_not_awaited()

        lock_directory_mock.assert_not_called()
        upload_mock.assert_not_awaited()
        delete_mock.assert_not_awaited()
        write_audit_mock.assert_not_awaited()
        emit_mock.assert_not_awaited()

    async def test_uploads_file_and_emits_hook(self):
        session = AsyncMock()
        user = self._build_user()
        uploaded = self._build_upload("document.txt")

        folder = self._build_folder()

        repository = AsyncMock()
        repository.select = AsyncMock(
            side_effect=[folder, None, None],
        )
        repository.select_parent_chain.return_value = ()

        config = MagicMock()
        config.FILES_DIR = "/mnt/files"

        lock_context = self._build_lock_context()
        main_path = "/mnt/files/documents/document.txt"

        with (
            patch(
                "app.services.file_upload.ORMRepository",
                return_value=repository,
            ),
            patch("app.models.file.get_config", return_value=config),
            patch("app.models.folder.get_config", return_value=config),
            patch(
                "app.services.file_upload.locks.lock_directory",
                return_value=lock_context,
            ) as lock_directory_mock,
            patch(
                "app.services.file_upload.get_tmp_path",
                return_value=STAGED_TMP,
            ),
            patch(
                "app.services.file_upload.upload",
                new=AsyncMock()
            ) as upload_mock,
            patch(
                "app.services.file_upload.copy",
                new=AsyncMock()
            ) as copy_mock,
            patch(
                "app.services.file_upload.get_filesize",
                new=AsyncMock(return_value=123)
            ) as filesize_mock,
            patch(
                "app.services.file_upload.get_mimetype",
                new=AsyncMock(return_value="text/plain")
            ) as mimetype_mock,
            patch(
                "app.services.file_upload.get_checksum",
                new=AsyncMock(return_value="a" * 64)
            ) as checksum_mock,
            patch(
                "app.services.file_upload.delete",
                new=AsyncMock()
            ) as delete_mock,
            patch(
                "app.services.file_upload.write_audit",
                new=AsyncMock()
            ) as write_audit_mock,
            patch(
                "app.services.file_upload.hooks.emit",
                new=AsyncMock()
            ) as emit_mock,
            patch(
                "app.services.file_upload.isdir",
                new=AsyncMock(return_value=False),
            ),
            patch(
                "app.services.file_upload.isfile",
                new=AsyncMock(return_value=False),
            ),
        ):
            result = await upload_file(session, user, 1, uploaded)

        self.assertIsInstance(result, File)
        self.assertEqual(result.folder_id, 1)
        self.assertEqual(result.created_by, 10)
        self.assertEqual(result.filename, "document.txt")
        self.assertEqual(result.filesize, 123)
        self.assertEqual(result.mimetype, "text/plain")
        self.assertEqual(result.checksum, "a" * 64)
        self.assertIsNone(result.summary)

        repository.select_parent_chain.assert_awaited_once_with(folder)

        lock_directory_mock.assert_called_once_with(
            "/mnt/files/documents",
            LockType.WRITE,
        )

        upload_mock.assert_awaited_once_with(uploaded, STAGED_TMP)
        copy_mock.assert_awaited_once_with(STAGED_TMP, main_path)
        filesize_mock.assert_awaited_once_with(STAGED_TMP)
        mimetype_mock.assert_awaited_once_with(STAGED_TMP)
        checksum_mock.assert_awaited_once_with(STAGED_TMP)

        repository.insert.assert_awaited_once_with(result)

        self.assertEqual(folder.files_count, 1)
        repository.update.assert_awaited_once_with(folder)

        write_audit_mock.assert_awaited_once_with(
            repository=repository,
            event=E.FILE_UPLOAD_COMPLETED,
            resource_type=File.__tablename__,
            resource_id=result.id,
        )

        repository.rollback.assert_not_awaited()
        repository.commit.assert_awaited_once()
        delete_mock.assert_awaited_once_with(STAGED_TMP)

        emit_mock.assert_awaited_once_with(
            E.FILE_UPLOAD_COMPLETED,
            session,
            result,
        )

    async def test_increments_folder_files_count_from_existing_value(self):
        session = AsyncMock()
        user = self._build_user()
        uploaded = self._build_upload("document.txt")

        folder = self._build_folder()
        folder.files_count = 20

        repository = AsyncMock()
        repository.select = AsyncMock(
            side_effect=[folder, None, None],
        )
        repository.select_parent_chain.return_value = ()

        config = MagicMock()
        config.FILES_DIR = "/mnt/files"

        lock_context = self._build_lock_context()

        with (
            patch(
                "app.services.file_upload.ORMRepository",
                return_value=repository,
            ),
            patch("app.models.file.get_config", return_value=config),
            patch("app.models.folder.get_config", return_value=config),
            patch(
                "app.services.file_upload.locks.lock_directory",
                return_value=lock_context,
            ),
            patch(
                "app.services.file_upload.get_tmp_path",
                return_value=STAGED_TMP,
            ),
            patch("app.services.file_upload.upload", new=AsyncMock()),
            patch("app.services.file_upload.copy", new=AsyncMock()),
            patch(
                "app.services.file_upload.get_filesize",
                new=AsyncMock(return_value=123),
            ),
            patch(
                "app.services.file_upload.get_mimetype",
                new=AsyncMock(return_value="text/plain"),
            ),
            patch(
                "app.services.file_upload.get_checksum",
                new=AsyncMock(return_value="a" * 64),
            ),
            patch("app.services.file_upload.delete", new=AsyncMock()),
            patch("app.services.file_upload.write_audit", new=AsyncMock()),
            patch("app.services.file_upload.hooks.emit", new=AsyncMock()),
            patch(
                "app.services.file_upload.isdir",
                new=AsyncMock(return_value=False),
            ),
            patch(
                "app.services.file_upload.isfile",
                new=AsyncMock(return_value=False),
            ),
        ):
            await upload_file(session, user, 1, uploaded)

        self.assertEqual(folder.files_count, 21)
        repository.update.assert_awaited_once_with(folder)

    async def test_rolls_back_and_cleans_up_on_insert_integrity_error(self):
        session = AsyncMock()
        user = self._build_user()
        uploaded = self._build_upload("document.txt")

        folder = self._build_folder()

        repository = AsyncMock()
        repository.select = AsyncMock(side_effect=[folder, None])
        repository.select_parent_chain.return_value = ()
        repository.insert.side_effect = IntegrityError(None, None, None)

        config = MagicMock()
        config.FILES_DIR = "/mnt/files"

        lock_context = self._build_lock_context()
        main_path = "/mnt/files/documents/document.txt"

        with (
            patch(
                "app.services.file_upload.ORMRepository",
                return_value=repository,
            ),
            patch("app.models.file.get_config", return_value=config),
            patch("app.models.folder.get_config", return_value=config),
            patch(
                "app.services.file_upload.locks.lock_directory",
                return_value=lock_context,
            ),
            patch(
                "app.services.file_upload.get_tmp_path",
                return_value=STAGED_TMP,
            ),
            patch(
                "app.services.file_upload.upload",
                new=AsyncMock()
            ) as upload_mock,
            patch(
                "app.services.file_upload.copy",
                new=AsyncMock()
            ) as copy_mock,
            patch(
                "app.services.file_upload.get_filesize",
                new=AsyncMock(return_value=123)
            ),
            patch(
                "app.services.file_upload.get_mimetype",
                new=AsyncMock(return_value="text/plain")
            ),
            patch(
                "app.services.file_upload.get_checksum",
                new=AsyncMock(return_value="a" * 64)
            ),
            patch(
                "app.services.file_upload.delete",
                new=AsyncMock()
            ) as delete_mock,
            patch(
                "app.services.file_upload.write_audit",
                new=AsyncMock()
            ) as write_audit_mock,
            patch(
                "app.services.file_upload.hooks.emit",
                new=AsyncMock()
            ) as emit_mock,
            patch(
                "app.services.file_upload.isdir",
                new=AsyncMock(return_value=False),
            ),
            patch(
                "app.services.file_upload.isfile",
                new=AsyncMock(return_value=False),
            ),
        ):
            with self.assertRaises(IntegrityError):
                await upload_file(session, user, 1, uploaded)

        upload_mock.assert_awaited_once_with(uploaded, STAGED_TMP)
        copy_mock.assert_awaited_once_with(STAGED_TMP, main_path)
        repository.insert.assert_awaited_once()
        repository.update.assert_not_awaited()
        repository.rollback.assert_awaited_once()
        repository.commit.assert_not_awaited()

        self.assertEqual(folder.files_count, 0)

        deleted_paths = [c.args[0] for c in delete_mock.await_args_list]
        self.assertEqual(deleted_paths, [STAGED_TMP, main_path])
        write_audit_mock.assert_not_awaited()
        emit_mock.assert_not_awaited()

    async def test_rolls_back_without_cleanup_when_upload_fails(self):
        session = AsyncMock()
        user = self._build_user()
        uploaded = self._build_upload("document.txt")

        folder = self._build_folder()

        repository = AsyncMock()
        repository.select.return_value = folder
        repository.select_parent_chain.return_value = ()

        config = MagicMock()
        config.FILES_DIR = "/mnt/files"

        lock_context = self._build_lock_context()
        error = RuntimeError("upload failed")

        with (
            patch(
                "app.services.file_upload.ORMRepository",
                return_value=repository,
            ),
            patch("app.models.file.get_config", return_value=config),
            patch("app.models.folder.get_config", return_value=config),
            patch(
                "app.services.file_upload.locks.lock_directory",
                return_value=lock_context,
            ) as lock_directory_mock,
            patch(
                "app.services.file_upload.get_tmp_path",
                return_value=STAGED_TMP,
            ),
            patch(
                "app.services.file_upload.upload",
                new=AsyncMock(side_effect=error)
            ) as upload_mock,
            patch(
                "app.services.file_upload.delete",
                new=AsyncMock()
            ) as delete_mock,
            patch(
                "app.services.file_upload.write_audit",
                new=AsyncMock()
            ) as write_audit_mock,
            patch(
                "app.services.file_upload.hooks.emit",
                new=AsyncMock()
            ) as emit_mock,
            patch(
                "app.services.file_upload.isdir",
                new=AsyncMock(return_value=False),
            ),
            patch(
                "app.services.file_upload.isfile",
                new=AsyncMock(return_value=False),
            ),
        ):
            with self.assertRaises(RuntimeError) as cm:
                await upload_file(session, user, 1, uploaded)

        self.assertIs(cm.exception, error)

        upload_mock.assert_awaited_once_with(uploaded, STAGED_TMP)
        repository.insert.assert_not_awaited()
        repository.update.assert_not_awaited()
        repository.rollback.assert_not_awaited()
        repository.commit.assert_not_awaited()

        lock_directory_mock.assert_not_called()
        delete_mock.assert_awaited_once_with(STAGED_TMP)
        write_audit_mock.assert_not_awaited()
        emit_mock.assert_not_awaited()

    async def test_rolls_back_and_cleanup_when_audit_fails_after_upload(self):
        session = AsyncMock()
        user = self._build_user()
        uploaded = self._build_upload("document.txt")

        folder = self._build_folder()

        repository = AsyncMock()
        repository.select = AsyncMock(side_effect=[folder, None])
        repository.select_parent_chain.return_value = ()

        config = MagicMock()
        config.FILES_DIR = "/mnt/files"

        lock_context = self._build_lock_context()
        error = RuntimeError("audit failed")
        main_path = "/mnt/files/documents/document.txt"

        with (
            patch(
                "app.services.file_upload.ORMRepository",
                return_value=repository,
            ),
            patch("app.models.file.get_config", return_value=config),
            patch("app.models.folder.get_config", return_value=config),
            patch(
                "app.services.file_upload.locks.lock_directory",
                return_value=lock_context,
            ),
            patch(
                "app.services.file_upload.get_tmp_path",
                return_value=STAGED_TMP,
            ),
            patch(
                "app.services.file_upload.upload",
                new=AsyncMock()
            ) as upload_mock,
            patch(
                "app.services.file_upload.copy",
                new=AsyncMock()
            ) as copy_mock,
            patch(
                "app.services.file_upload.get_filesize",
                new=AsyncMock(return_value=123)
            ),
            patch(
                "app.services.file_upload.get_mimetype",
                new=AsyncMock(return_value="text/plain")
            ),
            patch(
                "app.services.file_upload.get_checksum",
                new=AsyncMock(return_value="a" * 64)
            ),
            patch(
                "app.services.file_upload.delete",
                new=AsyncMock()
            ) as delete_mock,
            patch(
                "app.services.file_upload.write_audit",
                new=AsyncMock(side_effect=error)
            ) as write_audit_mock,
            patch(
                "app.services.file_upload.hooks.emit",
                new=AsyncMock()
            ) as emit_mock,
            patch(
                "app.services.file_upload.isdir",
                new=AsyncMock(return_value=False),
            ),
            patch(
                "app.services.file_upload.isfile",
                new=AsyncMock(return_value=False),
            ),
        ):
            with self.assertRaises(RuntimeError) as cm:
                await upload_file(session, user, 1, uploaded)

        self.assertIs(cm.exception, error)

        upload_mock.assert_awaited_once_with(uploaded, STAGED_TMP)
        copy_mock.assert_awaited_once_with(STAGED_TMP, main_path)
        repository.insert.assert_awaited_once()
        self.assertEqual(folder.files_count, 1)
        repository.update.assert_awaited_once_with(folder)
        write_audit_mock.assert_awaited_once()
        repository.rollback.assert_awaited_once()
        repository.commit.assert_not_awaited()

        deleted_paths = [c.args[0] for c in delete_mock.await_args_list]
        self.assertEqual(deleted_paths, [STAGED_TMP, main_path])
        emit_mock.assert_not_awaited()

    async def test_raises_conflict_when_path_too_long(self):
        session = AsyncMock()
        user = self._build_user()
        uploaded = self._build_upload("document.txt")

        folder = self._build_folder()

        repository = AsyncMock()
        repository.select.return_value = folder
        repository.select_parent_chain.return_value = ()

        config = MagicMock()
        config.FILES_DIR = "/mnt/files"

        with (
            patch("app.services.file_upload.FILES_MAX_PATH_LENGTH_BYTES", 1),
            patch(
                "app.services.file_upload.ORMRepository",
                return_value=repository,
            ),
            patch("app.models.file.get_config", return_value=config),
            patch("app.models.folder.get_config", return_value=config),
            patch(
                "app.services.file_upload.locks.lock_directory",
            ) as lock_directory_mock,
            patch(
                "app.services.file_upload.upload",
                new=AsyncMock()
            ) as upload_mock,
            patch(
                "app.services.file_upload.delete",
                new=AsyncMock()
            ) as delete_mock,
            patch(
                "app.services.file_upload.write_audit",
                new=AsyncMock()
            ) as write_audit_mock,
            patch(
                "app.services.file_upload.hooks.emit",
                new=AsyncMock()
            ) as emit_mock,
            patch(
                "app.services.file_upload.isdir",
                new=AsyncMock(return_value=False),
            ),
            patch(
                "app.services.file_upload.isfile",
                new=AsyncMock(return_value=False),
            ),
        ):
            with self.assertRaises(ResourceConflictError):
                await upload_file(session, user, 1, uploaded)

        repository.insert.assert_not_awaited()
        repository.update.assert_not_awaited()
        repository.rollback.assert_not_awaited()
        repository.commit.assert_not_awaited()

        lock_directory_mock.assert_not_called()
        upload_mock.assert_not_awaited()
        delete_mock.assert_not_awaited()
        write_audit_mock.assert_not_awaited()
        emit_mock.assert_not_awaited()

    async def test_raises_conflict_when_filesystem_file_exists(self):
        session = AsyncMock()
        user = self._build_user()
        uploaded = self._build_upload("document.txt")

        folder = self._build_folder()

        repository = AsyncMock()
        repository.select = AsyncMock(side_effect=[folder, None])
        repository.select_parent_chain.return_value = ()

        config = MagicMock()
        config.FILES_DIR = "/mnt/files"

        lock_context = self._build_lock_context()

        with (
            patch(
                "app.services.file_upload.ORMRepository",
                return_value=repository,
            ),
            patch("app.models.file.get_config", return_value=config),
            patch("app.models.folder.get_config", return_value=config),
            patch(
                "app.services.file_upload.locks.lock_directory",
                return_value=lock_context,
            ) as lock_directory_mock,
            patch(
                "app.services.file_upload.get_tmp_path",
                return_value=STAGED_TMP,
            ),
            patch(
                "app.services.file_upload.isdir",
                new=AsyncMock(return_value=False),
            ) as isdir_mock,
            patch(
                "app.services.file_upload.isfile",
                new=AsyncMock(return_value=True),
            ) as isfile_mock,
            patch(
                "app.services.file_upload.upload",
                new=AsyncMock()
            ) as upload_mock,
            patch(
                "app.services.file_upload.get_filesize",
                new=AsyncMock(return_value=1),
            ),
            patch(
                "app.services.file_upload.get_mimetype",
                new=AsyncMock(return_value="text/plain"),
            ),
            patch(
                "app.services.file_upload.get_checksum",
                new=AsyncMock(return_value="c" * 64),
            ),
            patch(
                "app.services.file_upload.delete",
                new=AsyncMock()
            ) as delete_mock,
            patch(
                "app.services.file_upload.write_audit",
                new=AsyncMock(),
            ) as write_audit_mock,
            patch(
                "app.services.file_upload.hooks.emit",
                new=AsyncMock(),
            ) as emit_mock,
        ):
            with self.assertRaises(ResourceConflictError):
                await upload_file(session, user, 1, uploaded)

        lock_directory_mock.assert_called_once_with(
            "/mnt/files/documents",
            LockType.WRITE,
        )

        isdir_mock.assert_awaited_once_with(
            "/mnt/files/documents/document.txt",
        )
        isfile_mock.assert_awaited_once_with(
            "/mnt/files/documents/document.txt",
        )

        upload_mock.assert_awaited_once_with(uploaded, STAGED_TMP)
        repository.insert.assert_not_awaited()
        repository.update.assert_not_awaited()
        repository.rollback.assert_not_awaited()
        repository.commit.assert_not_awaited()
        delete_mock.assert_awaited_once_with(STAGED_TMP)
        write_audit_mock.assert_not_awaited()
        emit_mock.assert_not_awaited()

    async def test_revision_upload_commits_and_emits_hook(self):
        session = AsyncMock()
        user = self._build_user()
        uploaded = self._build_upload("document.txt")
        folder = self._build_folder()
        existing = self._build_existing_file_mock()

        repository = AsyncMock()
        repository.select = AsyncMock(
            side_effect=[folder, existing, None],
        )
        repository.select_parent_chain.return_value = ()
        repository.count_all = AsyncMock(return_value=0)

        config = MagicMock()
        config.FILES_DIR = "/mnt/files"
        config.FILES_REVISIONS_DIR = "/mnt/revisions"

        fixed_uuid = uuid.UUID("12345678-1234-5678-1234-567812345678")
        rev_disk_path = (
            "/mnt/revisions/12345678-1234-5678-1234-567812345678"
        )
        main_path = "/mnt/files/documents/document.txt"

        lock_context = self._build_lock_context()

        with (
            patch(
                "app.services.file_upload.ORMRepository",
                return_value=repository,
            ),
            patch("app.models.file.get_config", return_value=config),
            patch("app.models.folder.get_config", return_value=config),
            patch(
                "app.models.file_revision.get_config",
                return_value=config,
            ),
            patch(
                "app.services.file_upload.uuid.uuid4",
                return_value=fixed_uuid,
            ),
            patch(
                "app.services.file_upload.locks.lock_directory",
                return_value=lock_context,
            ),
            patch(
                "app.services.file_upload.get_tmp_path",
                return_value=STAGED_TMP,
            ),
            patch(
                "app.services.file_upload.upload",
                new=AsyncMock(),
            ),
            patch(
                "app.services.file_upload.copy",
                new=AsyncMock(),
            ) as copy_mock,
            patch(
                "app.services.file_upload.get_filesize",
                new=AsyncMock(return_value=200),
            ),
            patch(
                "app.services.file_upload.get_mimetype",
                new=AsyncMock(return_value="text/plain"),
            ),
            patch(
                "app.services.file_upload.get_checksum",
                new=AsyncMock(return_value="d" * 64),
            ),
            patch(
                "app.services.file_upload.delete",
                new=AsyncMock(),
            ) as delete_mock,
            patch(
                "app.services.file_upload.write_audit",
                new=AsyncMock(),
            ),
            patch(
                "app.services.file_upload.hooks.emit",
                new=AsyncMock(),
            ) as emit_mock,
            patch(
                "app.services.file_upload.isdir",
                new=AsyncMock(return_value=False),
            ),
            patch(
                "app.services.file_upload.isfile",
                new=AsyncMock(return_value=False),
            ),
        ):
            result = await upload_file(session, user, 1, uploaded)

        self.assertIs(result, existing)
        self.assertEqual(copy_mock.await_count, 2)
        self.assertEqual(
            copy_mock.await_args_list[0].args,
            (main_path, rev_disk_path),
        )
        self.assertEqual(
            copy_mock.await_args_list[1].args,
            (STAGED_TMP, main_path),
        )

        repository.count_all.assert_awaited_once_with(
            FileRevision,
            file_id=42,
        )

        repository.insert.assert_awaited_once()
        inserted = repository.insert.await_args[0][0]
        self.assertEqual(inserted.__tablename__, "files_revisions")
        self.assertEqual(inserted.revision_number, 1)

        repository.update.assert_awaited_once_with(existing)
        self.assertEqual(existing.latest_revision_number, 1)
        self.assertEqual(folder.files_count, 0)
        repository.commit.assert_awaited_once()
        delete_mock.assert_awaited_once_with(STAGED_TMP)
        emit_mock.assert_awaited_once_with(
            E.FILE_UPLOAD_COMPLETED,
            session,
            existing,
        )

    async def test_revision_number_is_count_all_plus_one(self):
        session = AsyncMock()
        user = self._build_user()
        uploaded = self._build_upload("document.txt")
        folder = self._build_folder()
        existing = self._build_existing_file_mock()

        repository = AsyncMock()
        repository.select = AsyncMock(
            side_effect=[folder, existing, None],
        )
        repository.select_parent_chain.return_value = ()
        repository.count_all = AsyncMock(return_value=7)

        config = MagicMock()
        config.FILES_DIR = "/mnt/files"
        config.FILES_REVISIONS_DIR = "/mnt/revisions"

        fixed_uuid = uuid.UUID("12345678-1234-5678-1234-567812345678")

        lock_context = self._build_lock_context()

        with (
            patch(
                "app.services.file_upload.ORMRepository",
                return_value=repository,
            ),
            patch("app.models.file.get_config", return_value=config),
            patch("app.models.folder.get_config", return_value=config),
            patch(
                "app.models.file_revision.get_config",
                return_value=config,
            ),
            patch(
                "app.services.file_upload.uuid.uuid4",
                return_value=fixed_uuid,
            ),
            patch(
                "app.services.file_upload.locks.lock_directory",
                return_value=lock_context,
            ),
            patch(
                "app.services.file_upload.get_tmp_path",
                return_value=STAGED_TMP,
            ),
            patch("app.services.file_upload.upload", new=AsyncMock()),
            patch("app.services.file_upload.copy", new=AsyncMock()),
            patch(
                "app.services.file_upload.get_filesize",
                new=AsyncMock(return_value=200),
            ),
            patch(
                "app.services.file_upload.get_mimetype",
                new=AsyncMock(return_value="text/plain"),
            ),
            patch(
                "app.services.file_upload.get_checksum",
                new=AsyncMock(return_value="d" * 64),
            ),
            patch("app.services.file_upload.delete", new=AsyncMock()),
            patch("app.services.file_upload.write_audit", new=AsyncMock()),
            patch("app.services.file_upload.hooks.emit", new=AsyncMock()),
            patch(
                "app.services.file_upload.isdir",
                new=AsyncMock(return_value=False),
            ),
            patch(
                "app.services.file_upload.isfile",
                new=AsyncMock(return_value=False),
            ),
        ):
            await upload_file(session, user, 1, uploaded)

        repository.count_all.assert_awaited_once_with(
            FileRevision,
            file_id=42,
        )
        inserted = repository.insert.await_args[0][0]
        self.assertEqual(inserted.revision_number, 8)
        self.assertEqual(existing.latest_revision_number, 8)

    async def test_revision_succeeds_when_existing_and_upload_mime_are_none(
        self,
    ):
        """
        Neither DB nor probed upload MIME: inequality check is skipped
        (None == None), so revision is allowed without filename_conflict.
        """
        session = AsyncMock()
        user = self._build_user()
        uploaded = self._build_upload("document.bin")
        folder = self._build_folder()
        existing = self._build_existing_file_mock()
        existing.filename = "document.bin"
        existing.mimetype = None

        repository = AsyncMock()
        repository.select = AsyncMock(
            side_effect=[folder, existing, None],
        )
        repository.select_parent_chain.return_value = ()
        repository.count_all = AsyncMock(return_value=0)

        config = MagicMock()
        config.FILES_DIR = "/mnt/files"
        config.FILES_REVISIONS_DIR = "/mnt/revisions"

        fixed_uuid = uuid.UUID("12345678-1234-5678-1234-567812345678")

        lock_context = self._build_lock_context()

        with (
            patch(
                "app.services.file_upload.ORMRepository",
                return_value=repository,
            ),
            patch("app.models.file.get_config", return_value=config),
            patch("app.models.folder.get_config", return_value=config),
            patch(
                "app.models.file_revision.get_config",
                return_value=config,
            ),
            patch(
                "app.services.file_upload.uuid.uuid4",
                return_value=fixed_uuid,
            ),
            patch(
                "app.services.file_upload.locks.lock_directory",
                return_value=lock_context,
            ),
            patch(
                "app.services.file_upload.get_tmp_path",
                return_value=STAGED_TMP,
            ),
            patch(
                "app.services.file_upload.upload",
                new=AsyncMock(),
            ),
            patch(
                "app.services.file_upload.copy",
                new=AsyncMock(),
            ),
            patch(
                "app.services.file_upload.get_filesize",
                new=AsyncMock(return_value=200),
            ),
            patch(
                "app.services.file_upload.get_mimetype",
                new=AsyncMock(return_value=None),
            ),
            patch(
                "app.services.file_upload.get_checksum",
                new=AsyncMock(return_value="d" * 64),
            ),
            patch(
                "app.services.file_upload.delete",
                new=AsyncMock(),
            ),
            patch(
                "app.services.file_upload.write_audit",
                new=AsyncMock(),
            ),
            patch(
                "app.services.file_upload.hooks.emit",
                new=AsyncMock(),
            ),
            patch(
                "app.services.file_upload.isdir",
                new=AsyncMock(return_value=False),
            ),
            patch(
                "app.services.file_upload.isfile",
                new=AsyncMock(return_value=False),
            ),
        ):
            result = await upload_file(session, user, 1, uploaded)

        self.assertIs(result, existing)
        self.assertIsNone(existing.mimetype)

        repository.count_all.assert_awaited_once_with(
            FileRevision,
            file_id=42,
        )
        inserted_rev = repository.insert.await_args[0][0]
        self.assertEqual(inserted_rev.revision_number, 1)
        self.assertEqual(existing.latest_revision_number, 1)

        repository.update.assert_awaited_once_with(existing)
        self.assertEqual(folder.files_count, 0)
        repository.commit.assert_awaited_once()

    async def test_revision_rollback_before_main_replace_removes_backup_only(
        self,
    ):
        session = AsyncMock()
        user = self._build_user()
        uploaded = self._build_upload("document.txt")
        folder = self._build_folder()
        existing = self._build_existing_file_mock()

        repository = AsyncMock()
        repository.select = AsyncMock(side_effect=[folder, existing])
        repository.select_parent_chain.return_value = ()
        repository.count_all = AsyncMock(return_value=0)
        repository.insert.side_effect = IntegrityError(None, None, None)

        config = MagicMock()
        config.FILES_DIR = "/mnt/files"
        config.FILES_REVISIONS_DIR = "/mnt/revisions"

        fixed_uuid = uuid.UUID("12345678-1234-5678-1234-567812345678")
        rev_disk_path = (
            "/mnt/revisions/12345678-1234-5678-1234-567812345678"
        )
        main_path = "/mnt/files/documents/document.txt"

        lock_context = self._build_lock_context()

        with (
            patch(
                "app.services.file_upload.ORMRepository",
                return_value=repository,
            ),
            patch("app.models.file.get_config", return_value=config),
            patch("app.models.folder.get_config", return_value=config),
            patch(
                "app.models.file_revision.get_config",
                return_value=config,
            ),
            patch(
                "app.services.file_upload.uuid.uuid4",
                return_value=fixed_uuid,
            ),
            patch(
                "app.services.file_upload.locks.lock_directory",
                return_value=lock_context,
            ),
            patch(
                "app.services.file_upload.get_tmp_path",
                return_value=STAGED_TMP,
            ),
            patch("app.services.file_upload.upload", new=AsyncMock()),
            patch(
                "app.services.file_upload.copy",
                new=AsyncMock(),
            ) as copy_mock,
            patch(
                "app.services.file_upload.get_filesize",
                new=AsyncMock(return_value=200),
            ),
            patch(
                "app.services.file_upload.get_mimetype",
                new=AsyncMock(return_value="text/plain"),
            ),
            patch(
                "app.services.file_upload.get_checksum",
                new=AsyncMock(return_value="d" * 64),
            ),
            patch(
                "app.services.file_upload.delete",
                new=AsyncMock(),
            ) as delete_mock,
            patch("app.services.file_upload.write_audit", new=AsyncMock()),
            patch("app.services.file_upload.hooks.emit", new=AsyncMock()),
            patch(
                "app.services.file_upload.isdir",
                new=AsyncMock(return_value=False),
            ),
            patch(
                "app.services.file_upload.isfile",
                new=AsyncMock(return_value=False),
            ),
        ):
            with self.assertRaises(IntegrityError):
                await upload_file(session, user, 1, uploaded)

        repository.count_all.assert_awaited_once_with(
            FileRevision,
            file_id=42,
        )
        self.assertEqual(existing.latest_revision_number, 0)

        copy_mock.assert_awaited_once_with(main_path, rev_disk_path)
        deleted_paths = [c.args[0] for c in delete_mock.await_args_list]
        self.assertEqual(deleted_paths, [STAGED_TMP, rev_disk_path])

    async def test_revision_rollback_after_main_replace_restores_and_removes_backup(  # noqa: E501
        self,
    ):
        session = AsyncMock()
        user = self._build_user()
        uploaded = self._build_upload("document.txt")
        folder = self._build_folder()
        existing = self._build_existing_file_mock()

        repository = AsyncMock()
        repository.select = AsyncMock(side_effect=[folder, existing])
        repository.select_parent_chain.return_value = ()
        repository.count_all = AsyncMock(return_value=0)
        repository.update.side_effect = RuntimeError("update failed")

        config = MagicMock()
        config.FILES_DIR = "/mnt/files"
        config.FILES_REVISIONS_DIR = "/mnt/revisions"

        fixed_uuid = uuid.UUID("12345678-1234-5678-1234-567812345678")
        rev_disk_path = (
            "/mnt/revisions/12345678-1234-5678-1234-567812345678"
        )
        main_path = "/mnt/files/documents/document.txt"

        lock_context = self._build_lock_context()

        with (
            patch(
                "app.services.file_upload.ORMRepository",
                return_value=repository,
            ),
            patch("app.models.file.get_config", return_value=config),
            patch("app.models.folder.get_config", return_value=config),
            patch(
                "app.models.file_revision.get_config",
                return_value=config,
            ),
            patch(
                "app.services.file_upload.uuid.uuid4",
                return_value=fixed_uuid,
            ),
            patch(
                "app.services.file_upload.locks.lock_directory",
                return_value=lock_context,
            ),
            patch(
                "app.services.file_upload.get_tmp_path",
                return_value=STAGED_TMP,
            ),
            patch("app.services.file_upload.upload", new=AsyncMock()),
            patch(
                "app.services.file_upload.copy",
                new=AsyncMock(),
            ) as copy_mock,
            patch(
                "app.services.file_upload.get_filesize",
                new=AsyncMock(return_value=200),
            ),
            patch(
                "app.services.file_upload.get_mimetype",
                new=AsyncMock(return_value="text/plain"),
            ),
            patch(
                "app.services.file_upload.get_checksum",
                new=AsyncMock(return_value="d" * 64),
            ),
            patch(
                "app.services.file_upload.delete",
                new=AsyncMock(),
            ) as delete_mock,
            patch("app.services.file_upload.write_audit", new=AsyncMock()),
            patch("app.services.file_upload.hooks.emit", new=AsyncMock()),
            patch(
                "app.services.file_upload.isdir",
                new=AsyncMock(return_value=False),
            ),
            patch(
                "app.services.file_upload.isfile",
                new=AsyncMock(return_value=False),
            ),
        ):
            with self.assertRaises(RuntimeError):
                await upload_file(session, user, 1, uploaded)

        repository.count_all.assert_awaited_once_with(
            FileRevision,
            file_id=42,
        )
        self.assertEqual(existing.latest_revision_number, 1)

        self.assertEqual(copy_mock.await_count, 3)
        self.assertEqual(
            copy_mock.await_args_list[2].args,
            (rev_disk_path, main_path),
        )
        deleted_paths = [c.args[0] for c in delete_mock.await_args_list]
        self.assertEqual(deleted_paths, [STAGED_TMP, rev_disk_path])

    async def test_revision_rollback_restore_failure_keeps_backup_file(self):
        session = AsyncMock()
        user = self._build_user()
        uploaded = self._build_upload("document.txt")
        folder = self._build_folder()
        existing = self._build_existing_file_mock()

        repository = AsyncMock()
        repository.select = AsyncMock(side_effect=[folder, existing])
        repository.select_parent_chain.return_value = ()
        repository.count_all = AsyncMock(return_value=0)
        repository.update.side_effect = RuntimeError("update failed")

        config = MagicMock()
        config.FILES_DIR = "/mnt/files"
        config.FILES_REVISIONS_DIR = "/mnt/revisions"

        fixed_uuid = uuid.UUID("12345678-1234-5678-1234-567812345678")
        rev_disk_path = (
            "/mnt/revisions/12345678-1234-5678-1234-567812345678"
        )
        lock_context = self._build_lock_context()

        with (
            patch(
                "app.services.file_upload.ORMRepository",
                return_value=repository,
            ),
            patch("app.models.file.get_config", return_value=config),
            patch("app.models.folder.get_config", return_value=config),
            patch(
                "app.models.file_revision.get_config",
                return_value=config,
            ),
            patch(
                "app.services.file_upload.uuid.uuid4",
                return_value=fixed_uuid,
            ),
            patch(
                "app.services.file_upload.locks.lock_directory",
                return_value=lock_context,
            ),
            patch(
                "app.services.file_upload.get_tmp_path",
                return_value=STAGED_TMP,
            ),
            patch("app.services.file_upload.upload", new=AsyncMock()),
            patch(
                "app.services.file_upload.copy",
                new=AsyncMock(
                    side_effect=[
                        None,
                        None,
                        RuntimeError("restore failed"),
                    ],
                ),
            ) as copy_mock,
            patch(
                "app.services.file_upload.get_filesize",
                new=AsyncMock(return_value=200),
            ),
            patch(
                "app.services.file_upload.get_mimetype",
                new=AsyncMock(return_value="text/plain"),
            ),
            patch(
                "app.services.file_upload.get_checksum",
                new=AsyncMock(return_value="d" * 64),
            ),
            patch(
                "app.services.file_upload.delete",
                new=AsyncMock(),
            ) as delete_mock,
            patch("app.services.file_upload.write_audit", new=AsyncMock()),
            patch("app.services.file_upload.hooks.emit", new=AsyncMock()),
            patch(
                "app.services.file_upload.log.exception",
                MagicMock(),
            ),
            patch(
                "app.services.file_upload.isdir",
                new=AsyncMock(return_value=False),
            ),
            patch(
                "app.services.file_upload.isfile",
                new=AsyncMock(return_value=False),
            ),
        ):
            with self.assertRaises(RuntimeError):
                await upload_file(session, user, 1, uploaded)

        repository.count_all.assert_awaited_once_with(
            FileRevision,
            file_id=42,
        )
        self.assertEqual(existing.latest_revision_number, 1)

        self.assertEqual(copy_mock.await_count, 3)
        deleted_paths = [c.args[0] for c in delete_mock.await_args_list]
        self.assertEqual(deleted_paths, [STAGED_TMP])
        self.assertNotIn(rev_disk_path, deleted_paths)

    async def test_raises_conflict_when_target_path_is_directory(self):
        session = AsyncMock()
        user = self._build_user()
        uploaded = self._build_upload("document.txt")
        folder = self._build_folder()

        repository = AsyncMock()
        repository.select = AsyncMock(side_effect=[folder, None])
        repository.select_parent_chain.return_value = ()

        config = MagicMock()
        config.FILES_DIR = "/mnt/files"
        lock_context = self._build_lock_context()

        with (
            patch(
                "app.services.file_upload.ORMRepository",
                return_value=repository,
            ),
            patch("app.models.file.get_config", return_value=config),
            patch("app.models.folder.get_config", return_value=config),
            patch(
                "app.services.file_upload.locks.lock_directory",
                return_value=lock_context,
            ),
            patch(
                "app.services.file_upload.get_tmp_path",
                return_value=STAGED_TMP,
            ),
            patch(
                "app.services.file_upload.upload",
                new=AsyncMock(),
            ),
            patch(
                "app.services.file_upload.get_filesize",
                new=AsyncMock(return_value=1),
            ),
            patch(
                "app.services.file_upload.get_mimetype",
                new=AsyncMock(return_value="text/plain"),
            ),
            patch(
                "app.services.file_upload.get_checksum",
                new=AsyncMock(return_value="c" * 64),
            ),
            patch(
                "app.services.file_upload.isdir",
                new=AsyncMock(return_value=True),
            ) as isdir_mock,
            patch(
                "app.services.file_upload.isfile",
                new=AsyncMock(return_value=False),
            ),
            patch(
                "app.services.file_upload.delete",
                new=AsyncMock(),
            ) as delete_mock,
            patch(
                "app.services.file_upload.write_audit",
                new=AsyncMock(),
            ),
            patch(
                "app.services.file_upload.hooks.emit",
                new=AsyncMock(),
            ),
        ):
            with self.assertRaises(ResourceConflictError):
                await upload_file(session, user, 1, uploaded)

        isdir_mock.assert_awaited_once_with(
            "/mnt/files/documents/document.txt",
        )
        delete_mock.assert_awaited_once_with(STAGED_TMP)
        repository.update.assert_not_awaited()

    async def test_raises_conflict_when_existing_mimetype_mismatch(self):
        session = AsyncMock()
        user = self._build_user()
        uploaded = self._build_upload("document.txt")
        folder = self._build_folder()
        existing = self._build_existing_file_mock()
        existing.mimetype = "application/pdf"

        repository = AsyncMock()
        repository.select = AsyncMock(side_effect=[folder, existing])
        repository.select_parent_chain.return_value = ()

        config = MagicMock()
        config.FILES_DIR = "/mnt/files"
        lock_context = self._build_lock_context()

        with (
            patch(
                "app.services.file_upload.ORMRepository",
                return_value=repository,
            ),
            patch("app.models.file.get_config", return_value=config),
            patch("app.models.folder.get_config", return_value=config),
            patch(
                "app.services.file_upload.locks.lock_directory",
                return_value=lock_context,
            ),
            patch(
                "app.services.file_upload.get_tmp_path",
                return_value=STAGED_TMP,
            ),
            patch(
                "app.services.file_upload.upload",
                new=AsyncMock(),
            ),
            patch(
                "app.services.file_upload.get_filesize",
                new=AsyncMock(return_value=10),
            ),
            patch(
                "app.services.file_upload.get_mimetype",
                new=AsyncMock(return_value="text/plain"),
            ),
            patch(
                "app.services.file_upload.get_checksum",
                new=AsyncMock(return_value="c" * 64),
            ),
            patch(
                "app.services.file_upload.isdir",
                new=AsyncMock(return_value=False),
            ),
            patch(
                "app.services.file_upload.isfile",
                new=AsyncMock(return_value=False),
            ),
            patch(
                "app.services.file_upload.delete",
                new=AsyncMock(),
            ) as delete_mock,
            patch(
                "app.services.file_upload.write_audit",
                new=AsyncMock(),
            ),
            patch(
                "app.services.file_upload.hooks.emit",
                new=AsyncMock(),
            ),
        ):
            with self.assertRaises(ResourceConflictError):
                await upload_file(session, user, 1, uploaded)

        delete_mock.assert_awaited_once_with(STAGED_TMP)
        repository.update.assert_not_awaited()

    async def test_new_file_image_upload_inserts_thumbnail(self):
        session = AsyncMock()
        user = self._build_user()
        uploaded = self._build_upload("photo.png")
        folder = self._build_folder()

        repository = AsyncMock()
        repository.select = AsyncMock(
            side_effect=[folder, None, None],
        )
        repository.select_parent_chain.return_value = ()

        async def insert_assign_id(obj, flush=True, commit=False):
            if getattr(obj, "__tablename__", None) == "files":
                obj.id = 900

        repository.insert = AsyncMock(side_effect=insert_assign_id)

        config = MagicMock()
        config.FILES_DIR = "/mnt/files"
        config.FILES_THUMBNAILS_DIR = "/mnt/thumbs"

        thumb_uuid = uuid.UUID("aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee")
        thumb_disk = (
            "/mnt/thumbs/aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"
        )
        main_path = "/mnt/files/documents/photo.png"

        lock_context = self._build_lock_context()

        with (
            patch(
                "app.services.file_upload.ORMRepository",
                return_value=repository,
            ),
            patch("app.models.file.get_config", return_value=config),
            patch("app.models.folder.get_config", return_value=config),
            patch(
                "app.models.file_thumbnail.get_config",
                return_value=config,
            ),
            patch(
                "app.services.file_upload.uuid.uuid4",
                return_value=thumb_uuid,
            ),
            patch(
                "app.services.file_upload.locks.lock_directory",
                return_value=lock_context,
            ),
            patch(
                "app.services.file_upload.get_tmp_path",
                return_value=STAGED_TMP,
            ),
            patch(
                "app.services.file_upload.upload",
                new=AsyncMock(),
            ),
            patch(
                "app.services.file_upload.copy",
                new=AsyncMock(),
            ) as copy_mock,
            patch(
                "app.services.file_upload.get_filesize",
                new=AsyncMock(side_effect=[200, 400]),
            ) as filesize_mock,
            patch(
                "app.services.file_upload.get_mimetype",
                new=AsyncMock(side_effect=["image/png", "image/jpeg"]),
            ) as mimetype_mock,
            patch(
                "app.services.file_upload.get_checksum",
                new=AsyncMock(return_value="e" * 64),
            ),
            patch(
                "app.services.file_upload.create_thumbnail",
                new=AsyncMock(),
            ) as thumb_create_mock,
            patch(
                "app.services.file_upload.get_image_size",
                new=AsyncMock(return_value=(64, 48)),
            ) as image_size_mock,
            patch(
                "app.services.file_upload.delete",
                new=AsyncMock(),
            ) as delete_mock,
            patch(
                "app.services.file_upload.write_audit",
                new=AsyncMock(),
            ),
            patch(
                "app.services.file_upload.hooks.emit",
                new=AsyncMock(),
            ),
            patch(
                "app.services.file_upload.isdir",
                new=AsyncMock(return_value=False),
            ),
            patch(
                "app.services.file_upload.isfile",
                new=AsyncMock(return_value=False),
            ),
        ):
            await upload_file(session, user, 1, uploaded)

        copy_mock.assert_awaited_once_with(STAGED_TMP, main_path)
        thumb_create_mock.assert_awaited_once_with(main_path, thumb_disk)
        self.assertEqual(repository.insert.await_count, 2)
        thumb_row = repository.insert.await_args_list[1].args[0]
        self.assertEqual(thumb_row.__tablename__, "files_thumbnails")
        self.assertEqual(folder.files_count, 1)
        repository.update.assert_awaited_once_with(folder)
        filesize_mock.assert_awaited()
        mimetype_mock.assert_awaited()
        image_size_mock.assert_awaited_once_with(thumb_disk)
        delete_mock.assert_awaited_once_with(STAGED_TMP)

    async def test_revision_image_detaches_old_thumbnail_and_deletes_after_commit(  # noqa: E501
        self,
    ):
        session = AsyncMock()
        user = self._build_user()
        uploaded = self._build_upload("photo.png")
        folder = self._build_folder()
        existing = self._build_existing_file_mock()
        existing.filename = "photo.png"
        existing.mimetype = "image/png"
        old_thumb = MagicMock()
        old_thumb.absolute_path = "/mnt/thumbs/prev-thumb"

        async def select_side_effect(cls, obj_id=None, **filters):
            if cls is Folder:
                return folder
            if cls is File:
                return existing
            if cls is FileThumbnail:
                return old_thumb
            return None

        repository = AsyncMock()
        repository.select = AsyncMock(side_effect=select_side_effect)
        repository.select_parent_chain.return_value = ()
        repository.count_all = AsyncMock(return_value=0)

        config = MagicMock()
        config.FILES_DIR = "/mnt/files"
        config.FILES_REVISIONS_DIR = "/mnt/revisions"
        config.FILES_THUMBNAILS_DIR = "/mnt/thumbs"

        rev_uuid = uuid.UUID("12345678-1234-5678-1234-567812345678")
        new_thumb_uuid = uuid.UUID("87654321-4321-4321-4321-876543218765")
        new_thumb_disk = (
            "/mnt/thumbs/87654321-4321-4321-4321-876543218765"
        )
        main_path = "/mnt/files/documents/photo.png"

        lock_context = self._build_lock_context()

        with (
            patch(
                "app.services.file_upload.ORMRepository",
                return_value=repository,
            ),
            patch("app.models.file.get_config", return_value=config),
            patch("app.models.folder.get_config", return_value=config),
            patch(
                "app.models.file_revision.get_config",
                return_value=config,
            ),
            patch(
                "app.models.file_thumbnail.get_config",
                return_value=config,
            ),
            patch(
                "app.services.file_upload.uuid.uuid4",
                side_effect=[rev_uuid, new_thumb_uuid],
            ),
            patch(
                "app.services.file_upload.locks.lock_directory",
                return_value=lock_context,
            ),
            patch(
                "app.services.file_upload.get_tmp_path",
                return_value=STAGED_TMP,
            ),
            patch(
                "app.services.file_upload.upload",
                new=AsyncMock(),
            ),
            patch(
                "app.services.file_upload.copy",
                new=AsyncMock(),
            ),
            patch(
                "app.services.file_upload.get_filesize",
                new=AsyncMock(side_effect=[200, 300, 400]),
            ),
            patch(
                "app.services.file_upload.get_mimetype",
                new=AsyncMock(
                    side_effect=["image/png", "image/jpeg", "image/jpeg"],
                ),
            ),
            patch(
                "app.services.file_upload.get_checksum",
                new=AsyncMock(return_value="f" * 64),
            ),
            patch(
                "app.services.file_upload.create_thumbnail",
                new=AsyncMock(),
            ) as thumb_create_mock,
            patch(
                "app.services.file_upload.get_image_size",
                new=AsyncMock(return_value=(80, 60)),
            ),
            patch(
                "app.services.file_upload.delete",
                new=AsyncMock(),
            ) as delete_mock,
            patch(
                "app.services.file_upload.write_audit",
                new=AsyncMock(),
            ),
            patch(
                "app.services.file_upload.hooks.emit",
                new=AsyncMock(),
            ),
            patch(
                "app.services.file_upload.isdir",
                new=AsyncMock(return_value=False),
            ),
            patch(
                "app.services.file_upload.isfile",
                new=AsyncMock(return_value=False),
            ),
        ):
            await upload_file(session, user, 1, uploaded)

        repository.count_all.assert_awaited_once_with(
            FileRevision,
            file_id=42,
        )
        rev_row = repository.insert.await_args_list[0].args[0]
        self.assertEqual(rev_row.revision_number, 1)
        self.assertEqual(existing.latest_revision_number, 1)

        thumb_create_mock.assert_awaited_once_with(main_path, new_thumb_disk)
        self.assertEqual(repository.update.await_count, 1)
        repository.delete.assert_awaited_once_with(old_thumb, flush=False)
        self.assertEqual(repository.commit.await_count, 3)
        self.assertIsNotNone(existing.file_thumbnail)
        self.assertIsNot(existing.file_thumbnail, old_thumb)
        self.assertEqual(
            existing.file_thumbnail.__tablename__,
            "files_thumbnails",
        )

        deleted_paths = [c.args[0] for c in delete_mock.await_args_list]
        self.assertIn(STAGED_TMP, deleted_paths)
        self.assertIn("/mnt/thumbs/prev-thumb", deleted_paths)

    async def test_revision_image_old_thumbnail_delete_failure_rolls_back_and_skips_new_thumb(  # noqa: E501
        self,
    ):
        """
        If ORM delete/commit for the previous thumbnail fails, rollback runs,
        the failure is logged, and new thumbnail creation is skipped.
        """
        session = AsyncMock()
        user = self._build_user()
        uploaded = self._build_upload("photo.png")
        folder = self._build_folder()
        existing = self._build_existing_file_mock()
        existing.filename = "photo.png"
        existing.mimetype = "image/png"
        old_thumb = MagicMock()
        old_thumb.absolute_path = "/mnt/thumbs/prev-thumb"

        async def select_side_effect(cls, obj_id=None, **filters):
            if cls is Folder:
                return folder
            if cls is File:
                return existing
            if cls is FileThumbnail:
                return old_thumb
            return None

        repository = AsyncMock()
        repository.select = AsyncMock(side_effect=select_side_effect)
        repository.select_parent_chain.return_value = ()
        repository.count_all = AsyncMock(return_value=0)
        repository.delete = AsyncMock(
            side_effect=RuntimeError("thumbnail row delete failed"),
        )

        config = MagicMock()
        config.FILES_DIR = "/mnt/files"
        config.FILES_REVISIONS_DIR = "/mnt/revisions"
        config.FILES_THUMBNAILS_DIR = "/mnt/thumbs"

        rev_uuid = uuid.UUID("12345678-1234-5678-1234-567812345678")

        lock_context = self._build_lock_context()

        with ExitStack() as stack:
            stack.enter_context(
                patch(
                    "app.services.file_upload.ORMRepository",
                    return_value=repository,
                ),
            )
            stack.enter_context(
                patch("app.models.file.get_config", return_value=config),
            )
            stack.enter_context(
                patch("app.models.folder.get_config", return_value=config),
            )
            stack.enter_context(
                patch(
                    "app.models.file_revision.get_config",
                    return_value=config,
                ),
            )
            stack.enter_context(
                patch(
                    "app.models.file_thumbnail.get_config",
                    return_value=config,
                ),
            )
            stack.enter_context(
                patch(
                    "app.services.file_upload.uuid.uuid4",
                    return_value=rev_uuid,
                ),
            )
            stack.enter_context(
                patch(
                    "app.services.file_upload.locks.lock_directory",
                    return_value=lock_context,
                ),
            )
            stack.enter_context(
                patch(
                    "app.services.file_upload.get_tmp_path",
                    return_value=STAGED_TMP,
                ),
            )
            stack.enter_context(
                patch("app.services.file_upload.upload", new=AsyncMock()),
            )
            stack.enter_context(
                patch("app.services.file_upload.copy", new=AsyncMock()),
            )
            stack.enter_context(
                patch(
                    "app.services.file_upload.get_filesize",
                    new=AsyncMock(side_effect=[200, 300, 400]),
                ),
            )
            stack.enter_context(
                patch(
                    "app.services.file_upload.get_mimetype",
                    new=AsyncMock(
                        side_effect=[
                            "image/png",
                            "image/jpeg",
                            "image/jpeg",
                        ],
                    ),
                ),
            )
            stack.enter_context(
                patch(
                    "app.services.file_upload.get_checksum",
                    new=AsyncMock(return_value="f" * 64),
                ),
            )
            thumb_create_mock = stack.enter_context(
                patch(
                    "app.services.file_upload.create_thumbnail",
                    new=AsyncMock(),
                ),
            )
            stack.enter_context(
                patch(
                    "app.services.file_upload.get_image_size",
                    new=AsyncMock(return_value=(80, 60)),
                ),
            )
            delete_mock = stack.enter_context(
                patch("app.services.file_upload.delete", new=AsyncMock()),
            )
            stack.enter_context(
                patch("app.services.file_upload.write_audit", new=AsyncMock()),
            )
            stack.enter_context(
                patch("app.services.file_upload.hooks.emit", new=AsyncMock()),
            )
            log_exception_mock = stack.enter_context(
                patch(
                    "app.services.file_upload.log.exception",
                    MagicMock(),
                ),
            )
            stack.enter_context(
                patch(
                    "app.services.file_upload.isdir",
                    new=AsyncMock(return_value=False),
                ),
            )
            stack.enter_context(
                patch(
                    "app.services.file_upload.isfile",
                    new=AsyncMock(return_value=False),
                ),
            )
            await upload_file(session, user, 1, uploaded)

        repository.count_all.assert_awaited_once_with(
            FileRevision,
            file_id=42,
        )
        self.assertEqual(existing.latest_revision_number, 1)

        repository.delete.assert_awaited_once_with(old_thumb, flush=False)
        repository.commit.assert_awaited_once()
        repository.rollback.assert_awaited_once()
        log_exception_mock.assert_called_once()
        self.assertEqual(
            log_exception_mock.call_args[0][0],
            "event=%s",
        )
        self.assertEqual(
            log_exception_mock.call_args[0][1],
            E.FILE_UPLOAD_THUMBNAIL_FAILED,
        )
        thumb_create_mock.assert_not_awaited()
        deleted_paths = [c.args[0] for c in delete_mock.await_args_list]
        self.assertIn(STAGED_TMP, deleted_paths)
        self.assertNotIn("/mnt/thumbs/prev-thumb", deleted_paths)

    async def test_image_upload_commits_when_thumbnail_insert_fails(self):
        session = AsyncMock()
        user = self._build_user()
        uploaded = self._build_upload("photo.png")
        folder = self._build_folder()

        repository = AsyncMock()
        repository.select = AsyncMock(
            side_effect=[folder, None, None],
        )
        repository.select_parent_chain.return_value = ()

        async def insert_assign_id(obj, flush=True, commit=False):
            if getattr(obj, "__tablename__", None) == "files":
                obj.id = 55
            if getattr(obj, "__tablename__", None) == "files_thumbnails":
                raise RuntimeError("thumb insert failed")

        repository.insert = AsyncMock(side_effect=insert_assign_id)

        config = MagicMock()
        config.FILES_DIR = "/mnt/files"
        config.FILES_THUMBNAILS_DIR = "/mnt/thumbs"

        thumb_uuid = uuid.UUID("bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb")
        thumb_disk = (
            "/mnt/thumbs/bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb"
        )

        lock_context = self._build_lock_context()

        with (
            patch(
                "app.services.file_upload.ORMRepository",
                return_value=repository,
            ),
            patch("app.models.file.get_config", return_value=config),
            patch("app.models.folder.get_config", return_value=config),
            patch(
                "app.models.file_thumbnail.get_config",
                return_value=config,
            ),
            patch(
                "app.services.file_upload.uuid.uuid4",
                return_value=thumb_uuid,
            ),
            patch(
                "app.services.file_upload.locks.lock_directory",
                return_value=lock_context,
            ),
            patch(
                "app.services.file_upload.get_tmp_path",
                return_value=STAGED_TMP,
            ),
            patch(
                "app.services.file_upload.upload",
                new=AsyncMock(),
            ),
            patch(
                "app.services.file_upload.copy",
                new=AsyncMock(),
            ),
            patch(
                "app.services.file_upload.get_filesize",
                new=AsyncMock(side_effect=[200, 300]),
            ),
            patch(
                "app.services.file_upload.get_mimetype",
                new=AsyncMock(side_effect=["image/png", "image/jpeg"]),
            ),
            patch(
                "app.services.file_upload.get_checksum",
                new=AsyncMock(return_value="e" * 64),
            ),
            patch(
                "app.services.file_upload.create_thumbnail",
                new=AsyncMock(),
            ),
            patch(
                "app.services.file_upload.get_image_size",
                new=AsyncMock(return_value=(10, 10)),
            ),
            patch(
                "app.services.file_upload.delete",
                new=AsyncMock(),
            ) as delete_mock,
            patch(
                "app.services.file_upload.write_audit",
                new=AsyncMock(),
            ),
            patch(
                "app.services.file_upload.hooks.emit",
                new=AsyncMock(),
            ),
            patch(
                "app.services.file_upload.log.exception",
                MagicMock(),
            ),
            patch(
                "app.services.file_upload.isdir",
                new=AsyncMock(return_value=False),
            ),
            patch(
                "app.services.file_upload.isfile",
                new=AsyncMock(return_value=False),
            ),
        ):
            await upload_file(session, user, 1, uploaded)

        self.assertEqual(folder.files_count, 1)
        repository.update.assert_awaited_once_with(folder)
        repository.commit.assert_awaited_once()
        repository.rollback.assert_awaited_once()
        deleted_paths = [c.args[0] for c in delete_mock.await_args_list]
        self.assertEqual(deleted_paths, [STAGED_TMP, thumb_disk])


class TestCleanupPath(unittest.IsolatedAsyncioTestCase):

    async def test_skips_when_path_none(self):
        with patch("app.services.file_upload.delete", new=AsyncMock()) as d:
            await _cleanup_path(None)
        d.assert_not_awaited()

    async def test_success_awaits_delete_and_logs(self):
        delete_mock = AsyncMock()
        with (
            patch("app.services.file_upload.delete", new=delete_mock),
            patch(
                "app.services.file_upload.log.info",
                MagicMock(),
            ) as log_info,
        ):
            await _cleanup_path("/tmp/staged")

        delete_mock.assert_awaited_once_with("/tmp/staged")
        log_info.assert_called_once()

    async def test_logs_exception_when_delete_raises(self):
        with (
            patch(
                "app.services.file_upload.delete",
                new=AsyncMock(side_effect=OSError("rm failed")),
            ),
            patch(
                "app.services.file_upload.log.exception",
                MagicMock(),
            ) as log_exc,
        ):
            await _cleanup_path("/tmp/x")

        log_exc.assert_called_once()
