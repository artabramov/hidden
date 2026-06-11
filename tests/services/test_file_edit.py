# tests/services/test_file_edit.py
# SPDX-License-Identifier: GPL-3.0-only

import unittest
import uuid
from unittest.mock import AsyncMock, MagicMock, call, mock_open, patch


from tests.helpers import set_minimal_app_config_env


set_minimal_app_config_env()

from app.errors import (  # noqa: E402
    ResourceConflictError,
    ResourceLockedError,
    ResourceNotFoundError,
)
from app.events import Events as E  # noqa: E402
from app.locks import LockType  # noqa: E402
from app.models.file import File  # noqa: E402
from app.models.file_revision import FileRevision  # noqa: E402
from app.models.folder import Folder  # noqa: E402
from app.models.user import User  # noqa: E402
from app.schemas.file_edit import FileEditRequest  # noqa: E402
from app.services.file_edit import _cleanup_path, _write_text, edit_file  # noqa: E501, E402
import app.services.file_edit as file_edit  # noqa: E402


class TestEditFile(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        super().setUp()
        self._log_patcher = patch(
            "app.services.file_edit.log",
            MagicMock(),
        )
        self._log_patcher.start()
        self.addCleanup(self._log_patcher.stop)

        self._uuid_patcher = patch(
            "app.services.file_edit.uuid.uuid4",
            return_value=uuid.UUID("00000000-0000-4000-8000-0000000000aa"),
        )
        self._uuid_patcher.start()
        self.addCleanup(self._uuid_patcher.stop)

    def _build_user(self):
        user = MagicMock(spec=User)
        user.id = 10
        return user

    def _build_folder(self):
        folder = MagicMock(spec=Folder)
        folder.id = 2
        folder.is_write_protected = False
        folder.is_write_protected_recursive.return_value = False
        return folder

    def _build_file(self, folder):
        file = MagicMock(spec=File)
        file.id = 1
        file.filename = "notes.txt"
        file.filesize = 100
        file.mimetype = "text/plain"
        file.checksum = "old-checksum"
        file.updated_by = None
        file.latest_revision_number = 0
        file.file_folder = folder
        file.get_absolute_path.return_value = "/mnt/files/folder/notes.txt"
        file.is_text = True
        return file

    def _build_lock_context(self):
        lock_context = AsyncMock()
        lock_context.__aenter__.return_value = None
        lock_context.__aexit__.return_value = None
        return lock_context

    async def test_edits_file_creates_revision_commits_and_emits_hook(self):
        session = AsyncMock()
        user = self._build_user()
        data = FileEditRequest(content="new text")

        folder = self._build_folder()
        file = self._build_file(folder)
        parent_chain = (MagicMock(),)

        revision = MagicMock(spec=FileRevision)
        revision.absolute_path = "/mnt/revisions/rev-1"

        repository = AsyncMock()
        repository.select.return_value = file
        repository.select_parent_chain.return_value = parent_chain
        repository.count_all.return_value = 0

        lock_context = self._build_lock_context()

        with (
            patch(
                "app.services.file_edit.ORMRepository",
                return_value=repository
            ),
            patch(
                "app.services.file_edit.locks.lock_file",
                return_value=lock_context,
            ) as lock_file_mock,
            patch(
                "app.services.file_edit.isdir",
                new=AsyncMock(return_value=False)
            ),
            patch(
                "app.services.file_edit.isfile",
                new=AsyncMock(return_value=True)
            ),
            patch(
                "app.services.file_edit.get_tmp_path",
                return_value="/tmp/edited"
            ),
            patch(
                "app.services.file_edit._write_text",
                new=AsyncMock()
            ) as write_mock,
            patch(
                "app.services.file_edit.get_filesize",
                new=AsyncMock(return_value=8),
            ) as get_filesize_mock,
            patch(
                "app.services.file_edit.get_checksum",
                new=AsyncMock(return_value="new-checksum"),
            ) as get_checksum_mock,
            patch(
                "app.services.file_edit.FileRevision",
                return_value=revision,
            ) as file_revision_mock,
            patch(
                "app.services.file_edit.copy",
                new=AsyncMock()
            ) as copy_mock,
            patch(
                "app.services.file_edit.delete",
                new=AsyncMock()
            ) as delete_mock,
            patch(
                "app.services.file_edit.write_audit",
                new=AsyncMock(),
            ) as write_audit_mock,
            patch(
                "app.services.file_edit.hooks.emit",
                new=AsyncMock()
            ) as emit_mock,
        ):
            result = await edit_file(session, user, 1, data)

        self.assertIs(result, file)

        repository.select.assert_awaited_once_with(File, obj_id=1)
        repository.select_parent_chain.assert_awaited_once_with(folder)
        folder.is_write_protected_recursive.assert_called_once_with(
            parent_chain
        )
        file.get_absolute_path.assert_called_once_with(folder, parent_chain)

        lock_file_mock.assert_called_once_with(
            "/mnt/files/folder/notes.txt",
            LockType.WRITE,
        )

        write_mock.assert_awaited_once_with("/tmp/edited", "new text")
        get_filesize_mock.assert_awaited_once_with("/tmp/edited")
        get_checksum_mock.assert_awaited_once_with("/tmp/edited")

        repository.count_all.assert_awaited_once_with(
            file_revision_mock,
            file_id=1,
        )

        self.assertEqual(file_revision_mock.call_args.kwargs["file_id"], 1)
        self.assertEqual(file_revision_mock.call_args.kwargs["created_by"], 10)
        self.assertEqual(
            file_revision_mock.call_args.kwargs["revision_number"],
            1
        )
        self.assertEqual(
            file_revision_mock.call_args.kwargs["filename"],
            "notes.txt"
        )
        self.assertEqual(file_revision_mock.call_args.kwargs["filesize"], 100)
        self.assertEqual(
            file_revision_mock.call_args.kwargs["mimetype"],
            "text/plain"
        )
        self.assertEqual(
            file_revision_mock.call_args.kwargs["checksum"],
            "old-checksum",
        )

        self.assertEqual(
            copy_mock.await_args_list,
            [
                call("/mnt/files/folder/notes.txt", "/mnt/revisions/rev-1"),
                call("/tmp/edited", "/mnt/files/folder/notes.txt"),
            ],
        )

        repository.insert.assert_awaited_once_with(revision)
        repository.update.assert_awaited_once_with(file)

        self.assertEqual(file.filesize, 8)
        self.assertEqual(file.mimetype, "text/plain")
        self.assertEqual(file.checksum, "new-checksum")
        self.assertEqual(file.updated_by, 10)
        self.assertEqual(file.latest_revision_number, 1)

        delete_mock.assert_awaited_once_with("/tmp/edited")

        write_audit_mock.assert_awaited_once_with(
            repository=repository,
            event=E.FILE_EDIT_COMPLETED,
            resource_type=File.__tablename__,
            resource_id=1,
        )
        repository.commit.assert_awaited_once()
        repository.rollback.assert_not_awaited()

        emit_mock.assert_awaited_once_with(
            E.FILE_EDIT_COMPLETED,
            session,
            file,
        )

    async def test_raises_not_found(self):
        session = AsyncMock()
        user = self._build_user()
        data = FileEditRequest(content="new text")

        repository = AsyncMock()
        repository.select.return_value = None

        with (
            patch(
                "app.services.file_edit.ORMRepository",
                return_value=repository
            ),
            patch(
                "app.services.file_edit.hooks.emit",
                new=AsyncMock()
            ) as emit_mock,
        ):
            with self.assertRaises(ResourceNotFoundError):
                await edit_file(session, user, 1, data)

        repository.select.assert_awaited_once_with(File, obj_id=1)
        repository.select_parent_chain.assert_not_awaited()
        repository.commit.assert_not_awaited()
        repository.rollback.assert_not_awaited()
        emit_mock.assert_not_awaited()

    async def test_raises_conflict_when_file_is_not_text(self):
        session = AsyncMock()
        user = self._build_user()
        data = FileEditRequest(content="new text")

        folder = self._build_folder()
        file = self._build_file(folder)
        file.mimetype = "image/png"
        file.is_text = False

        repository = AsyncMock()
        repository.select.return_value = file

        with (
            patch(
                "app.services.file_edit.ORMRepository",
                return_value=repository
            ),
            patch(
                "app.services.file_edit.hooks.emit",
                new=AsyncMock()
            ) as emit_mock,
        ):
            with self.assertRaises(ResourceConflictError):
                await edit_file(session, user, 1, data)

        repository.select_parent_chain.assert_not_awaited()
        repository.commit.assert_not_awaited()
        repository.rollback.assert_not_awaited()
        emit_mock.assert_not_awaited()

    async def test_raises_locked_when_parent_folder_is_protected(self):
        session = AsyncMock()
        user = self._build_user()
        data = FileEditRequest(content="new text")

        folder = self._build_folder()
        folder.is_write_protected_recursive.return_value = True
        file = self._build_file(folder)
        parent_chain = (MagicMock(),)

        repository = AsyncMock()
        repository.select.return_value = file
        repository.select_parent_chain.return_value = parent_chain

        with (
            patch(
                "app.services.file_edit.ORMRepository",
                return_value=repository
            ),
            patch(
                "app.services.file_edit.hooks.emit",
                new=AsyncMock()
            ) as emit_mock,
        ):
            with self.assertRaises(ResourceLockedError):
                await edit_file(session, user, 1, data)

        folder.is_write_protected_recursive.assert_called_once_with(
            parent_chain
        )
        repository.commit.assert_not_awaited()
        repository.rollback.assert_not_awaited()
        emit_mock.assert_not_awaited()

    async def test_raises_conflict_when_path_is_directory(self):
        session = AsyncMock()
        user = self._build_user()
        data = FileEditRequest(content="new text")

        folder = self._build_folder()
        file = self._build_file(folder)

        repository = AsyncMock()
        repository.select.return_value = file
        repository.select_parent_chain.return_value = ()

        lock_context = self._build_lock_context()

        with (
            patch(
                "app.services.file_edit.ORMRepository",
                return_value=repository
            ),
            patch(
                "app.services.file_edit.locks.lock_file",
                return_value=lock_context
            ),
            patch(
                "app.services.file_edit.isdir",
                new=AsyncMock(return_value=True),
            ) as isdir_mock,
            patch(
                "app.services.file_edit.isfile",
                new=AsyncMock()
            ) as isfile_mock,
            patch(
                "app.services.file_edit._write_text",
                new=AsyncMock(),
            ) as write_mock,
            patch(
                "app.services.file_edit.hooks.emit",
                new=AsyncMock()
            ) as emit_mock,
        ):
            with self.assertRaises(ResourceConflictError):
                await edit_file(session, user, 1, data)

        isdir_mock.assert_awaited_once_with("/mnt/files/folder/notes.txt")
        isfile_mock.assert_not_awaited()
        write_mock.assert_not_awaited()
        repository.commit.assert_not_awaited()
        repository.rollback.assert_not_awaited()
        emit_mock.assert_not_awaited()

    async def test_raises_conflict_when_file_missing_on_disk(self):
        session = AsyncMock()
        user = self._build_user()
        data = FileEditRequest(content="new text")

        folder = self._build_folder()
        file = self._build_file(folder)

        repository = AsyncMock()
        repository.select.return_value = file
        repository.select_parent_chain.return_value = ()

        lock_context = self._build_lock_context()

        with (
            patch(
                "app.services.file_edit.ORMRepository",
                return_value=repository
            ),
            patch(
                "app.services.file_edit.locks.lock_file",
                return_value=lock_context
            ),
            patch(
                "app.services.file_edit.isdir",
                new=AsyncMock(return_value=False)
            ),
            patch(
                "app.services.file_edit.isfile",
                new=AsyncMock(return_value=False),
            ) as isfile_mock,
            patch(
                "app.services.file_edit._write_text",
                new=AsyncMock(),
            ) as write_mock,
            patch(
                "app.services.file_edit.hooks.emit",
                new=AsyncMock()
            ) as emit_mock,
        ):
            with self.assertRaises(ResourceConflictError):
                await edit_file(session, user, 1, data)

        isfile_mock.assert_awaited_once_with("/mnt/files/folder/notes.txt")
        write_mock.assert_not_awaited()
        repository.commit.assert_not_awaited()
        repository.rollback.assert_not_awaited()
        emit_mock.assert_not_awaited()

    async def test_write_failure_raises_conflict_and_cleans_tmp(self):
        session = AsyncMock()
        user = self._build_user()
        data = FileEditRequest(content="new text")

        folder = self._build_folder()
        file = self._build_file(folder)

        repository = AsyncMock()
        repository.select.return_value = file
        repository.select_parent_chain.return_value = ()

        lock_context = self._build_lock_context()

        with (
            patch(
                "app.services.file_edit.ORMRepository",
                return_value=repository
            ),
            patch(
                "app.services.file_edit.locks.lock_file",
                return_value=lock_context
            ),
            patch(
                "app.services.file_edit.isdir",
                new=AsyncMock(return_value=False)
            ),
            patch(
                "app.services.file_edit.isfile",
                new=AsyncMock(return_value=True)
            ),
            patch(
                "app.services.file_edit.get_tmp_path",
                return_value="/tmp/edited"
            ),
            patch(
                "app.services.file_edit._write_text",
                new=AsyncMock(side_effect=OSError("write failed")),
            ),
            patch(
                "app.services.file_edit.delete",
                new=AsyncMock()
            ) as delete_mock,
            patch(
                "app.services.file_edit.hooks.emit",
                new=AsyncMock()
            ) as emit_mock,
        ):
            with self.assertRaises(ResourceConflictError):
                await edit_file(session, user, 1, data)

        delete_mock.assert_awaited_once_with("/tmp/edited")
        repository.insert.assert_not_awaited()
        repository.update.assert_not_awaited()
        repository.commit.assert_not_awaited()
        repository.rollback.assert_not_awaited()
        emit_mock.assert_not_awaited()

    async def test_rollback_deletes_revision_insert_fails_before_replace(self):
        session = AsyncMock()
        user = self._build_user()
        data = FileEditRequest(content="new text")

        folder = self._build_folder()
        file = self._build_file(folder)

        revision = MagicMock(spec=FileRevision)
        revision.absolute_path = "/mnt/revisions/rev-1"

        repository = AsyncMock()
        repository.select.return_value = file
        repository.select_parent_chain.return_value = ()
        repository.count_all.return_value = 0
        repository.insert.side_effect = RuntimeError("db failed")

        lock_context = self._build_lock_context()

        with (
            patch(
                "app.services.file_edit.ORMRepository",
                return_value=repository
            ),
            patch(
                "app.services.file_edit.locks.lock_file",
                return_value=lock_context
            ),
            patch(
                "app.services.file_edit.isdir",
                new=AsyncMock(return_value=False)
            ),
            patch(
                "app.services.file_edit.isfile",
                new=AsyncMock(return_value=True)
            ),
            patch(
                "app.services.file_edit.get_tmp_path",
                return_value="/tmp/edited"
            ),
            patch(
                "app.services.file_edit._write_text",
                new=AsyncMock()
            ),
            patch(
                "app.services.file_edit.get_filesize",
                new=AsyncMock(return_value=8)
            ),
            patch(
                "app.services.file_edit.get_checksum",
                new=AsyncMock(return_value="new-checksum"),
            ),
            patch(
                "app.services.file_edit.FileRevision",
                return_value=revision
            ),
            patch(
                "app.services.file_edit.copy",
                new=AsyncMock()
            ) as copy_mock,
            patch(
                "app.services.file_edit.delete",
                new=AsyncMock()
            ) as delete_mock,
            patch(
                "app.services.file_edit.write_audit",
                new=AsyncMock(),
            ) as write_audit_mock,
            patch(
                "app.services.file_edit.hooks.emit",
                new=AsyncMock()
            ) as emit_mock,
        ):
            with self.assertRaises(RuntimeError):
                await edit_file(session, user, 1, data)

        copy_mock.assert_awaited_once_with(
            "/mnt/files/folder/notes.txt",
            "/mnt/revisions/rev-1",
        )
        repository.rollback.assert_awaited_once()
        delete_mock.assert_has_awaits([
            call("/tmp/edited"),
            call("/mnt/revisions/rev-1"),
        ])
        write_audit_mock.assert_not_awaited()
        repository.commit.assert_not_awaited()
        emit_mock.assert_not_awaited()

    async def test_rolls_back_restores_original_when_error_after_replace(self):
        session = AsyncMock()
        user = self._build_user()
        data = FileEditRequest(content="new text")

        folder = self._build_folder()
        file = self._build_file(folder)

        revision = MagicMock(spec=FileRevision)
        revision.absolute_path = "/mnt/revisions/rev-1"

        repository = AsyncMock()
        repository.select.return_value = file
        repository.select_parent_chain.return_value = ()
        repository.count_all.return_value = 0
        repository.update.side_effect = RuntimeError("db failed")

        lock_context = self._build_lock_context()

        with (
            patch(
                "app.services.file_edit.ORMRepository",
                return_value=repository
            ),
            patch(
                "app.services.file_edit.locks.lock_file",
                return_value=lock_context
            ),
            patch(
                "app.services.file_edit.isdir",
                new=AsyncMock(return_value=False)
            ),
            patch(
                "app.services.file_edit.isfile",
                new=AsyncMock(return_value=True)
            ),
            patch(
                "app.services.file_edit.get_tmp_path",
                return_value="/tmp/edited"
            ),
            patch(
                "app.services.file_edit._write_text",
                new=AsyncMock()
            ),
            patch(
                "app.services.file_edit.get_filesize",
                new=AsyncMock(return_value=8)
            ),
            patch(
                "app.services.file_edit.get_checksum",
                new=AsyncMock(return_value="new-checksum"),
            ),
            patch(
                "app.services.file_edit.FileRevision",
                return_value=revision
            ),
            patch(
                "app.services.file_edit.copy",
                new=AsyncMock()
            ) as copy_mock,
            patch(
                "app.services.file_edit.delete",
                new=AsyncMock()
            ) as delete_mock,
            patch(
                "app.services.file_edit.write_audit",
                new=AsyncMock(),
            ) as write_audit_mock,
            patch(
                "app.services.file_edit.hooks.emit",
                new=AsyncMock()
            ) as emit_mock,
        ):
            with self.assertRaises(RuntimeError):
                await edit_file(session, user, 1, data)

        self.assertEqual(
            copy_mock.await_args_list,
            [
                call("/mnt/files/folder/notes.txt", "/mnt/revisions/rev-1"),
                call("/tmp/edited", "/mnt/files/folder/notes.txt"),
                call("/mnt/revisions/rev-1", "/mnt/files/folder/notes.txt"),
            ],
        )
        repository.rollback.assert_awaited_once()
        delete_mock.assert_has_awaits([
            call("/tmp/edited"),
            call("/mnt/revisions/rev-1"),
        ])
        write_audit_mock.assert_not_awaited()
        repository.commit.assert_not_awaited()
        emit_mock.assert_not_awaited()

    async def test_restore_copy_failure_and_preserves_original_exception(self):
        session = AsyncMock()
        user = self._build_user()
        data = FileEditRequest(content="new text")

        folder = self._build_folder()
        file = self._build_file(folder)

        revision = MagicMock(spec=FileRevision)
        revision.absolute_path = "/mnt/revisions/rev-1"

        repository = AsyncMock()
        repository.select.return_value = file
        repository.select_parent_chain.return_value = ()
        repository.count_all.return_value = 0
        repository.update.side_effect = RuntimeError("db failed")

        lock_context = self._build_lock_context()
        restore_error = OSError("restore failed")

        with (
            patch(
                "app.services.file_edit.ORMRepository",
                return_value=repository
            ),
            patch(
                "app.services.file_edit.locks.lock_file",
                return_value=lock_context
            ),
            patch(
                "app.services.file_edit.isdir",
                new=AsyncMock(return_value=False)
            ),
            patch(
                "app.services.file_edit.isfile",
                new=AsyncMock(return_value=True)
            ),
            patch(
                "app.services.file_edit.get_tmp_path",
                return_value="/tmp/edited"
            ),
            patch(
                "app.services.file_edit._write_text",
                new=AsyncMock()
            ),
            patch(
                "app.services.file_edit.get_filesize",
                new=AsyncMock(return_value=8)
            ),
            patch(
                "app.services.file_edit.get_checksum",
                new=AsyncMock(return_value="new-checksum"),
            ),
            patch(
                "app.services.file_edit.FileRevision",
                return_value=revision
            ),
            patch(
                "app.services.file_edit.copy",
                new=AsyncMock(side_effect=[None, None, restore_error]),
            ) as copy_mock,
            patch(
                "app.services.file_edit.delete",
                new=AsyncMock()
            ) as delete_mock,
            patch(
                "app.services.file_edit.write_audit",
                new=AsyncMock(),
            ) as write_audit_mock,
            patch(
                "app.services.file_edit.hooks.emit",
                new=AsyncMock()
            ) as emit_mock,
        ):
            with self.assertRaises(RuntimeError) as cm:
                await edit_file(session, user, 1, data)

        self.assertEqual(cm.exception.args[0], "db failed")
        self.assertEqual(
            copy_mock.await_args_list,
            [
                call("/mnt/files/folder/notes.txt", "/mnt/revisions/rev-1"),
                call("/tmp/edited", "/mnt/files/folder/notes.txt"),
                call("/mnt/revisions/rev-1", "/mnt/files/folder/notes.txt"),
            ],
        )
        repository.rollback.assert_awaited_once()
        delete_mock.assert_awaited_once_with("/tmp/edited")
        write_audit_mock.assert_not_awaited()
        repository.commit.assert_not_awaited()
        emit_mock.assert_not_awaited()

        file_edit.log.exception.assert_called()
        self.assertIn(
            E.FILE_EDIT_RESTORE_FAILED,
            file_edit.log.exception.call_args[0],
        )

    async def test_error_before_revision_path_set_skips_restore_cleanup(self):
        session = AsyncMock()
        user = self._build_user()
        data = FileEditRequest(content="new text")

        folder = self._build_folder()
        file = self._build_file(folder)

        revision = MagicMock(spec=FileRevision)
        revision.absolute_path = "/mnt/revisions/rev-1"

        repository = AsyncMock()
        repository.select.return_value = file
        repository.select_parent_chain.return_value = ()
        repository.count_all.return_value = 0

        lock_context = self._build_lock_context()

        with (
            patch(
                "app.services.file_edit.ORMRepository",
                return_value=repository
            ),
            patch(
                "app.services.file_edit.locks.lock_file",
                return_value=lock_context
            ),
            patch(
                "app.services.file_edit.isdir",
                new=AsyncMock(return_value=False)
            ),
            patch(
                "app.services.file_edit.isfile",
                new=AsyncMock(return_value=True)
            ),
            patch(
                "app.services.file_edit.get_tmp_path",
                return_value="/tmp/edited"
            ),
            patch(
                "app.services.file_edit._write_text",
                new=AsyncMock()
            ),
            patch(
                "app.services.file_edit.get_filesize",
                new=AsyncMock(return_value=8)
            ),
            patch(
                "app.services.file_edit.get_checksum",
                new=AsyncMock(return_value="new-checksum"),
            ),
            patch(
                "app.services.file_edit.FileRevision",
                return_value=revision
            ),
            patch(
                "app.services.file_edit.copy",
                new=AsyncMock(
                    side_effect=RuntimeError("revision copy failed")
                ),
            ) as copy_mock,
            patch(
                "app.services.file_edit.delete",
                new=AsyncMock()
            ) as delete_mock,
            patch(
                "app.services.file_edit.write_audit",
                new=AsyncMock(),
            ) as write_audit_mock,
            patch(
                "app.services.file_edit.hooks.emit",
                new=AsyncMock()
            ) as emit_mock,
        ):
            with self.assertRaises(RuntimeError) as cm:
                await edit_file(session, user, 1, data)

        self.assertEqual(cm.exception.args[0], "revision copy failed")
        copy_mock.assert_awaited_once_with(
            "/mnt/files/folder/notes.txt",
            "/mnt/revisions/rev-1",
        )
        repository.rollback.assert_awaited_once()
        delete_mock.assert_awaited_once_with("/tmp/edited")
        write_audit_mock.assert_not_awaited()
        repository.commit.assert_not_awaited()
        emit_mock.assert_not_awaited()

    async def test_cleanup_path_delete_failure_logs_cleanup_failed(self):
        with patch(
            "app.services.file_edit.delete",
            new=AsyncMock(side_effect=OSError("unlink failed")),
        ):
            await _cleanup_path("/mnt/ephemeral/stale")

        file_edit.log.exception.assert_called()
        self.assertIn(
            E.FILE_EDIT_CLEANUP_FAILED,
            file_edit.log.exception.call_args[0],
        )

    async def test_cleanup_path_no_op_when_path_is_none(self):
        with patch(
            "app.services.file_edit.delete",
            new=AsyncMock()
        ) as delete_mock:
            await _cleanup_path(None)

        delete_mock.assert_not_awaited()

    async def test_write_text_opens_utf8_and_writes_in_thread(self):
        async def fake_to_thread(fn):
            return fn()

        m_open = mock_open()

        with (
            patch(
                "app.services.file_edit.asyncio.to_thread",
                new=fake_to_thread
            ),
            patch("app.services.file_edit.open", m_open),
        ):
            await _write_text("/virtual/tmp.txt", "café")

        m_open.assert_called_once_with(
            "/virtual/tmp.txt",
            "w", encoding="utf-8"
        )
        m_open().write.assert_called_once_with("café")
