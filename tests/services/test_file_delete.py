# tests/services/test_file_delete.py
# SPDX-License-Identifier: GPL-3.0-only

import unittest
from unittest.mock import AsyncMock, MagicMock, call, patch

from app.errors import ResourceLockedError, ResourceNotFoundError
from app.events import Events as E
from app.locks import LockType
from app.models.file import File
from app.models.file_revision import FileRevision
from app.models.file_thumbnail import FileThumbnail
from app.services.file_delete import delete_file


TMP_PATH = "/mnt/files/.tmp/delete-file"


class TestDeleteFile(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        super().setUp()
        self.thumbnail_cache_mock = MagicMock()
        self._thumbnail_cache_patcher = patch(
            "app.services.file_delete.get_thumbnail_cache",
            return_value=self.thumbnail_cache_mock,
        )
        self._thumbnail_cache_patcher.start()
        self.addCleanup(self._thumbnail_cache_patcher.stop)

    def _build_lock_context(self):
        lock_context = AsyncMock()
        lock_context.__aenter__.return_value = None
        lock_context.__aexit__.return_value = None
        return lock_context

    def _build_folder(self):
        folder = MagicMock()
        folder.files_count = 3
        folder.is_write_protected = False
        folder.is_write_protected_recursive.return_value = False
        folder.get_absolute_dir.return_value = "/mnt/files/docs"
        return folder

    def _build_file(self, folder):
        file = MagicMock(spec=File)
        file.id = 42
        file.file_folder = folder
        file.get_absolute_path.return_value = "/mnt/files/docs/file.txt"
        return file

    def _build_revision(self, revision_id, path):
        revision = MagicMock(spec=FileRevision)
        revision.id = revision_id
        revision.absolute_path = path
        return revision

    def _build_thumbnail(self):
        thumbnail = MagicMock(spec=FileThumbnail)
        thumbnail.id = 77
        thumbnail.absolute_path = "/mnt/files/.thumbnails/file.webp"
        return thumbnail

    async def test_deletes_file_writes_audit_commits_cleanup_emits_hook(self):
        session = AsyncMock()

        folder = self._build_folder()
        file = self._build_file(folder)
        revisions = [
            self._build_revision(1, "/mnt/files/.revisions/1"),
            self._build_revision(2, "/mnt/files/.revisions/2"),
        ]
        thumbnail = self._build_thumbnail()
        parent_chain = (MagicMock(),)

        repository = AsyncMock()
        repository.select.side_effect = [file, thumbnail]
        repository.select_parent_chain.return_value = parent_chain
        repository.select_all.return_value = revisions

        lock_context = self._build_lock_context()

        with (
            patch(
                "app.services.file_delete.ORMRepository",
                return_value=repository,
            ),
            patch(
                "app.services.file_delete.locks.lock_directory",
                return_value=lock_context,
            ) as lock_directory_mock,
            patch(
                "app.services.file_delete.get_tmp_path",
                return_value=TMP_PATH,
            ),
            patch(
                "app.services.file_delete.rename",
                new=AsyncMock(),
            ) as rename_mock,
            patch(
                "app.services.file_delete.delete",
                new=AsyncMock(),
            ) as delete_mock,
            patch(
                "app.services.file_delete.write_audit",
                new=AsyncMock(),
            ) as write_audit_mock,
            patch(
                "app.services.file_delete.hooks.emit",
                new=AsyncMock(),
            ) as emit_mock,
        ):
            result = await delete_file(session=session, file_id=42)

        self.assertIs(result, file)

        self.assertEqual(
            repository.select.await_args_list,
            [
                call(File, obj_id=42),
                call(FileThumbnail, file_id=42),
            ],
        )
        repository.select_parent_chain.assert_awaited_once_with(folder)
        repository.select_all.assert_awaited_once_with(
            FileRevision,
            file_id=42,
        )

        folder.is_write_protected_recursive.assert_called_once_with(
            parent_chain,
        )
        file.get_absolute_path.assert_called_once_with(folder, parent_chain)
        folder.get_absolute_dir.assert_called_once_with(parent_chain)

        lock_directory_mock.assert_called_once_with(
            "/mnt/files/docs",
            LockType.WRITE,
        )
        lock_context.__aenter__.assert_awaited_once()
        lock_context.__aexit__.assert_awaited_once()

        rename_mock.assert_awaited_once_with(
            "/mnt/files/docs/file.txt",
            TMP_PATH,
        )

        self.assertEqual(
            repository.delete.await_args_list,
            [
                call(thumbnail),
                call(revisions[0]),
                call(revisions[1]),
                call(file),
            ],
        )

        self.assertEqual(folder.files_count, 2)
        repository.update.assert_awaited_once_with(folder)

        write_audit_mock.assert_awaited_once_with(
            repository=repository,
            event=E.FILE_DELETE_COMPLETED,
            resource_type=File.__tablename__,
            resource_id=42,
        )
        repository.commit.assert_awaited_once()
        repository.rollback.assert_not_awaited()

        self.thumbnail_cache_mock.evict.assert_called_once_with(42)

        self.assertEqual(
            delete_mock.await_args_list,
            [
                call(TMP_PATH),
                call("/mnt/files/.thumbnails/file.webp"),
                call("/mnt/files/.revisions/1"),
                call("/mnt/files/.revisions/2"),
            ],
        )

        emit_mock.assert_awaited_once_with(
            E.FILE_DELETE_COMPLETED,
            session,
            file,
        )

    async def test_raises_not_found_file_missing(self):
        session = AsyncMock()

        repository = AsyncMock()
        repository.select.return_value = None

        lock_context = self._build_lock_context()

        with (
            patch(
                "app.services.file_delete.ORMRepository",
                return_value=repository,
            ),
            patch(
                "app.services.file_delete.locks.lock_directory",
                return_value=lock_context,
            ) as lock_directory_mock,
            patch(
                "app.services.file_delete.rename",
                new=AsyncMock(),
            ) as rename_mock,
            patch(
                "app.services.file_delete.delete",
                new=AsyncMock(),
            ) as delete_mock,
            patch(
                "app.services.file_delete.write_audit",
                new=AsyncMock(),
            ) as write_audit_mock,
            patch(
                "app.services.file_delete.hooks.emit",
                new=AsyncMock(),
            ) as emit_mock,
        ):
            with self.assertRaises(ResourceNotFoundError):
                await delete_file(session=session, file_id=42)

        repository.select.assert_awaited_once_with(File, obj_id=42)
        repository.select_parent_chain.assert_not_awaited()
        repository.select_all.assert_not_awaited()
        repository.delete.assert_not_awaited()
        repository.update.assert_not_awaited()
        repository.commit.assert_not_awaited()
        repository.rollback.assert_not_awaited()

        lock_directory_mock.assert_not_called()
        lock_context.__aenter__.assert_not_awaited()
        rename_mock.assert_not_awaited()
        delete_mock.assert_not_awaited()
        write_audit_mock.assert_not_awaited()
        emit_mock.assert_not_awaited()

    async def test_raises_locked_parent_protected(self):
        session = AsyncMock()

        folder = self._build_folder()
        folder.is_write_protected_recursive.return_value = True

        file = self._build_file(folder)
        parent_chain = (MagicMock(),)

        repository = AsyncMock()
        repository.select.return_value = file
        repository.select_parent_chain.return_value = parent_chain

        lock_context = self._build_lock_context()

        with (
            patch(
                "app.services.file_delete.ORMRepository",
                return_value=repository,
            ),
            patch(
                "app.services.file_delete.locks.lock_directory",
                return_value=lock_context,
            ) as lock_directory_mock,
            patch(
                "app.services.file_delete.rename",
                new=AsyncMock(),
            ) as rename_mock,
            patch(
                "app.services.file_delete.delete",
                new=AsyncMock(),
            ) as delete_mock,
            patch(
                "app.services.file_delete.write_audit",
                new=AsyncMock(),
            ) as write_audit_mock,
            patch(
                "app.services.file_delete.hooks.emit",
                new=AsyncMock(),
            ) as emit_mock,
        ):
            with self.assertRaises(ResourceLockedError):
                await delete_file(session=session, file_id=42)

        repository.select.assert_awaited_once_with(File, obj_id=42)
        repository.select_parent_chain.assert_awaited_once_with(folder)
        folder.is_write_protected_recursive.assert_called_once_with(
            parent_chain,
        )

        repository.select_all.assert_not_awaited()
        repository.delete.assert_not_awaited()
        repository.update.assert_not_awaited()
        repository.commit.assert_not_awaited()
        repository.rollback.assert_not_awaited()

        lock_directory_mock.assert_not_called()
        lock_context.__aenter__.assert_not_awaited()
        rename_mock.assert_not_awaited()
        delete_mock.assert_not_awaited()
        write_audit_mock.assert_not_awaited()
        emit_mock.assert_not_awaited()

    async def test_rolls_back_and_restores_file_when_transaction_fails(self):
        session = AsyncMock()

        folder = self._build_folder()
        file = self._build_file(folder)
        parent_chain = (MagicMock(),)

        error = RuntimeError("delete failed")

        repository = AsyncMock()
        repository.select.side_effect = [file, None]
        repository.select_parent_chain.return_value = parent_chain
        repository.select_all.return_value = []
        repository.delete.side_effect = error

        lock_context = self._build_lock_context()

        with (
            patch(
                "app.services.file_delete.ORMRepository",
                return_value=repository,
            ),
            patch(
                "app.services.file_delete.locks.lock_directory",
                return_value=lock_context,
            ),
            patch(
                "app.services.file_delete.get_tmp_path",
                return_value=TMP_PATH,
            ),
            patch(
                "app.services.file_delete.rename",
                new=AsyncMock(),
            ) as rename_mock,
            patch(
                "app.services.file_delete.delete",
                new=AsyncMock(),
            ) as delete_mock,
            patch(
                "app.services.file_delete.write_audit",
                new=AsyncMock(),
            ) as write_audit_mock,
            patch(
                "app.services.file_delete.hooks.emit",
                new=AsyncMock(),
            ) as emit_mock,
        ):
            with self.assertRaises(RuntimeError) as cm:
                await delete_file(session=session, file_id=42)

        self.assertIs(cm.exception, error)

        self.assertEqual(
            rename_mock.await_args_list,
            [
                call("/mnt/files/docs/file.txt", TMP_PATH),
                call(TMP_PATH, "/mnt/files/docs/file.txt"),
            ],
        )

        repository.rollback.assert_awaited_once()
        repository.commit.assert_not_awaited()
        delete_mock.assert_not_awaited()
        write_audit_mock.assert_not_awaited()
        emit_mock.assert_not_awaited()

    async def test_rolls_back_and_cleans_tmp_when_restore_fails(self):
        session = AsyncMock()

        folder = self._build_folder()
        file = self._build_file(folder)
        parent_chain = (MagicMock(),)

        transaction_error = RuntimeError("delete failed")
        restore_error = RuntimeError("restore failed")

        repository = AsyncMock()
        repository.select.side_effect = [file, None]
        repository.select_parent_chain.return_value = parent_chain
        repository.select_all.return_value = []
        repository.delete.side_effect = transaction_error

        lock_context = self._build_lock_context()

        with (
            patch(
                "app.services.file_delete.ORMRepository",
                return_value=repository,
            ),
            patch(
                "app.services.file_delete.locks.lock_directory",
                return_value=lock_context,
            ),
            patch(
                "app.services.file_delete.get_tmp_path",
                return_value=TMP_PATH,
            ),
            patch(
                "app.services.file_delete.rename",
                new=AsyncMock(side_effect=[None, restore_error]),
            ) as rename_mock,
            patch(
                "app.services.file_delete.delete",
                new=AsyncMock(),
            ) as delete_mock,
            patch(
                "app.services.file_delete.write_audit",
                new=AsyncMock(),
            ) as write_audit_mock,
            patch(
                "app.services.file_delete.hooks.emit",
                new=AsyncMock(),
            ) as emit_mock,
        ):
            with self.assertRaises(RuntimeError) as cm:
                await delete_file(session=session, file_id=42)

        self.assertIs(cm.exception, transaction_error)

        self.assertEqual(
            rename_mock.await_args_list,
            [
                call("/mnt/files/docs/file.txt", TMP_PATH),
                call(TMP_PATH, "/mnt/files/docs/file.txt"),
            ],
        )
        delete_mock.assert_awaited_once_with(TMP_PATH)

        repository.rollback.assert_awaited_once()
        repository.commit.assert_not_awaited()
        write_audit_mock.assert_not_awaited()
        emit_mock.assert_not_awaited()

    async def test_logs_when_restore_and_cleanup_restore_fail(self):
        session = AsyncMock()

        folder = self._build_folder()
        file = self._build_file(folder)
        parent_chain = (MagicMock(),)

        transaction_error = RuntimeError("delete failed")
        restore_error = RuntimeError("restore failed")
        cleanup_restore_error = RuntimeError("cleanup restore failed")

        repository = AsyncMock()
        repository.select.side_effect = [file, None]
        repository.select_parent_chain.return_value = parent_chain
        repository.select_all.return_value = []
        repository.delete.side_effect = transaction_error

        lock_context = self._build_lock_context()

        with (
            patch(
                "app.services.file_delete.ORMRepository",
                return_value=repository,
            ),
            patch(
                "app.services.file_delete.locks.lock_directory",
                return_value=lock_context,
            ),
            patch(
                "app.services.file_delete.get_tmp_path",
                return_value=TMP_PATH,
            ),
            patch(
                "app.services.file_delete.rename",
                new=AsyncMock(side_effect=[None, restore_error]),
            ),
            patch(
                "app.services.file_delete.delete",
                new=AsyncMock(side_effect=cleanup_restore_error),
            ),
            patch(
                "app.services.file_delete.write_audit",
                new=AsyncMock(),
            ) as write_audit_mock,
            patch(
                "app.services.file_delete.hooks.emit",
                new=AsyncMock(),
            ) as emit_mock,
            patch(
                "app.services.file_delete.log.exception"
            ) as log_exception_mock,
        ):
            with self.assertRaises(RuntimeError) as cm:
                await delete_file(session=session, file_id=42)

        self.assertIs(cm.exception, transaction_error)

        self.assertEqual(log_exception_mock.call_count, 2)
        log_exception_mock.assert_has_calls(
            [
                call("event=%s", E.FILE_DELETE_RESTORE_FAILED),
                call("event=%s", E.FILE_DELETE_CLEANUP_TMP_FAILED),
            ],
        )

        repository.rollback.assert_awaited_once()
        repository.commit.assert_not_awaited()
        write_audit_mock.assert_not_awaited()
        emit_mock.assert_not_awaited()

    async def test_logs_restore_failure_when_rename_back_raises(self):
        session = AsyncMock()

        folder = self._build_folder()
        file = self._build_file(folder)
        parent_chain = (MagicMock(),)

        transaction_error = RuntimeError("delete failed")
        restore_error = RuntimeError("restore failed")

        repository = AsyncMock()
        repository.select.side_effect = [file, None]
        repository.select_parent_chain.return_value = parent_chain
        repository.select_all.return_value = []
        repository.delete.side_effect = transaction_error

        lock_context = self._build_lock_context()

        with (
            patch(
                "app.services.file_delete.ORMRepository",
                return_value=repository,
            ),
            patch(
                "app.services.file_delete.locks.lock_directory",
                return_value=lock_context,
            ),
            patch(
                "app.services.file_delete.get_tmp_path",
                return_value=TMP_PATH,
            ),
            patch(
                "app.services.file_delete.rename",
                new=AsyncMock(side_effect=[None, restore_error]),
            ) as rename_mock,
            patch(
                "app.services.file_delete.delete",
                new=AsyncMock(),
            ) as delete_mock,
            patch(
                "app.services.file_delete.log.exception"
            ) as log_exception_mock,
        ):
            with self.assertRaises(RuntimeError) as cm:
                await delete_file(session=session, file_id=42)

        self.assertIs(cm.exception, transaction_error)
        self.assertEqual(
            rename_mock.await_args_list,
            [
                call("/mnt/files/docs/file.txt", TMP_PATH),
                call(TMP_PATH, "/mnt/files/docs/file.txt"),
            ],
        )
        log_exception_mock.assert_called_once_with(
            "event=%s",
            E.FILE_DELETE_RESTORE_FAILED,
        )
        delete_mock.assert_awaited_once_with(TMP_PATH)

    async def test_cleanup_failures_after_commit_do_not_fail_operation(self):
        session = AsyncMock()

        folder = self._build_folder()
        file = self._build_file(folder)
        revisions = [
            self._build_revision(1, "/mnt/files/.revisions/1"),
        ]
        thumbnail = self._build_thumbnail()
        parent_chain = (MagicMock(),)

        repository = AsyncMock()
        repository.select.side_effect = [file, thumbnail]
        repository.select_parent_chain.return_value = parent_chain
        repository.select_all.return_value = revisions

        lock_context = self._build_lock_context()
        cleanup_error = RuntimeError("cleanup failed")

        with (
            patch(
                "app.services.file_delete.ORMRepository",
                return_value=repository,
            ),
            patch(
                "app.services.file_delete.locks.lock_directory",
                return_value=lock_context,
            ),
            patch(
                "app.services.file_delete.get_tmp_path",
                return_value=TMP_PATH,
            ),
            patch(
                "app.services.file_delete.rename",
                new=AsyncMock(),
            ),
            patch(
                "app.services.file_delete.delete",
                new=AsyncMock(side_effect=cleanup_error),
            ) as delete_mock,
            patch(
                "app.services.file_delete.write_audit",
                new=AsyncMock(),
            ),
            patch(
                "app.services.file_delete.hooks.emit",
                new=AsyncMock(),
            ) as emit_mock,
            patch(
                "app.services.file_delete.log.exception",
            ) as log_exception_mock,
        ):
            result = await delete_file(session=session, file_id=42)

        self.assertIs(result, file)

        repository.commit.assert_awaited_once()
        repository.rollback.assert_not_awaited()

        self.assertEqual(
            delete_mock.await_args_list,
            [
                call(TMP_PATH),
                call("/mnt/files/.thumbnails/file.webp"),
                call("/mnt/files/.revisions/1"),
            ],
        )

        self.assertEqual(log_exception_mock.call_count, 3)
        log_exception_mock.assert_has_calls(
            [
                call("event=%s", E.FILE_DELETE_CLEANUP_TMP_FAILED),
                call("event=%s", E.FILE_DELETE_CLEANUP_THUMBNAIL_FAILED),
                call("event=%s", E.FILE_DELETE_CLEANUP_REVISION_FAILED),
            ],
        )

        emit_mock.assert_awaited_once_with(
            E.FILE_DELETE_COMPLETED,
            session,
            file,
        )

    async def test_thumbnail_cleanup_branch_runs_when_thumbnail_exists(self):
        session = AsyncMock()

        folder = self._build_folder()
        file = self._build_file(folder)
        thumbnail = self._build_thumbnail()
        parent_chain = (MagicMock(),)

        repository = AsyncMock()
        repository.select.side_effect = [file, thumbnail]
        repository.select_parent_chain.return_value = parent_chain
        repository.select_all.return_value = []

        lock_context = self._build_lock_context()

        async def delete_side_effect(path):
            if path == thumbnail.absolute_path:
                raise RuntimeError("thumbnail cleanup failed")
            return None

        with (
            patch(
                "app.services.file_delete.ORMRepository",
                return_value=repository,
            ),
            patch(
                "app.services.file_delete.locks.lock_directory",
                return_value=lock_context,
            ),
            patch(
                "app.services.file_delete.get_tmp_path",
                return_value=TMP_PATH,
            ),
            patch(
                "app.services.file_delete.rename",
                new=AsyncMock(),
            ),
            patch(
                "app.services.file_delete.delete",
                new=AsyncMock(side_effect=delete_side_effect),
            ) as delete_mock,
            patch(
                "app.services.file_delete.write_audit",
                new=AsyncMock(),
            ),
            patch(
                "app.services.file_delete.hooks.emit",
                new=AsyncMock(),
            ),
            patch(
                "app.services.file_delete.log.exception"
            ) as log_exception_mock,
        ):
            result = await delete_file(session=session, file_id=42)

        self.assertIs(result, file)
        self.assertEqual(
            delete_mock.await_args_list,
            [
                call(TMP_PATH),
                call("/mnt/files/.thumbnails/file.webp"),
            ],
        )
        log_exception_mock.assert_called_once_with(
            "event=%s",
            E.FILE_DELETE_CLEANUP_THUMBNAIL_FAILED,
        )

    async def test_logs_thumbnail_cleanup_failure_after_commit(self):
        session = AsyncMock()

        folder = self._build_folder()
        file = self._build_file(folder)
        thumbnail = self._build_thumbnail()
        parent_chain = (MagicMock(),)

        repository = AsyncMock()
        repository.select.side_effect = [file, thumbnail]
        repository.select_parent_chain.return_value = parent_chain
        repository.select_all.return_value = []

        lock_context = self._build_lock_context()
        thumbnail_cleanup_error = RuntimeError("thumbnail cleanup failed")

        async def delete_side_effect(path):
            if path == thumbnail.absolute_path:
                raise thumbnail_cleanup_error
            return None

        with (
            patch(
                "app.services.file_delete.ORMRepository",
                return_value=repository,
            ),
            patch(
                "app.services.file_delete.locks.lock_directory",
                return_value=lock_context,
            ),
            patch(
                "app.services.file_delete.get_tmp_path",
                return_value=TMP_PATH,
            ),
            patch(
                "app.services.file_delete.rename",
                new=AsyncMock(),
            ),
            patch(
                "app.services.file_delete.delete",
                new=AsyncMock(side_effect=delete_side_effect),
            ) as delete_mock,
            patch(
                "app.services.file_delete.write_audit",
                new=AsyncMock(),
            ),
            patch(
                "app.services.file_delete.hooks.emit",
                new=AsyncMock(),
            ) as emit_mock,
            patch(
                "app.services.file_delete.log.exception"
            ) as log_exception_mock,
        ):
            result = await delete_file(session=session, file_id=42)

        self.assertIs(result, file)
        repository.commit.assert_awaited_once()
        repository.rollback.assert_not_awaited()

        self.assertEqual(
            delete_mock.await_args_list,
            [
                call(TMP_PATH),
                call("/mnt/files/.thumbnails/file.webp"),
            ],
        )

        log_exception_mock.assert_called_once_with(
            "event=%s",
            E.FILE_DELETE_CLEANUP_THUMBNAIL_FAILED,
        )
        emit_mock.assert_awaited_once_with(
            E.FILE_DELETE_COMPLETED,
            session,
            file,
        )

    async def test_rollback_when_move_to_tmp_fails_skips_restore_block(self):
        """file_moved stays False: inner restore try is skipped."""
        session = AsyncMock()

        folder = self._build_folder()
        file = self._build_file(folder)
        parent_chain = (MagicMock(),)
        move_error = RuntimeError("move to tmp failed")

        repository = AsyncMock()
        repository.select.side_effect = [file, None]
        repository.select_parent_chain.return_value = parent_chain
        repository.select_all.return_value = []

        lock_context = self._build_lock_context()

        with (
            patch(
                "app.services.file_delete.ORMRepository",
                return_value=repository,
            ),
            patch(
                "app.services.file_delete.locks.lock_directory",
                return_value=lock_context,
            ),
            patch(
                "app.services.file_delete.get_tmp_path",
                return_value=TMP_PATH,
            ),
            patch(
                "app.services.file_delete.rename",
                new=AsyncMock(side_effect=move_error),
            ) as rename_mock,
            patch(
                "app.services.file_delete.delete",
                new=AsyncMock(),
            ) as delete_mock,
            patch(
                "app.services.file_delete.write_audit",
                new=AsyncMock(),
            ),
            patch(
                "app.services.file_delete.hooks.emit",
                new=AsyncMock(),
            ),
        ):
            with self.assertRaises(RuntimeError) as cm:
                await delete_file(session=session, file_id=42)

        self.assertIs(cm.exception, move_error)
        rename_mock.assert_awaited_once_with(
            "/mnt/files/docs/file.txt",
            TMP_PATH,
        )
        repository.rollback.assert_awaited_once()
        repository.commit.assert_not_awaited()
        delete_mock.assert_awaited_once_with(TMP_PATH)

    async def test_success_cleanup_skips_thumbnail_delete_when_no_thumbnail(
        self,
    ):
        """After commit, thumbnail is None."""
        session = AsyncMock()

        folder = self._build_folder()
        file = self._build_file(folder)
        parent_chain = (MagicMock(),)

        repository = AsyncMock()
        repository.select.side_effect = [file, None]
        repository.select_parent_chain.return_value = parent_chain
        repository.select_all.return_value = []

        lock_context = self._build_lock_context()

        with (
            patch(
                "app.services.file_delete.ORMRepository",
                return_value=repository,
            ),
            patch(
                "app.services.file_delete.locks.lock_directory",
                return_value=lock_context,
            ),
            patch(
                "app.services.file_delete.get_tmp_path",
                return_value=TMP_PATH,
            ),
            patch(
                "app.services.file_delete.rename",
                new=AsyncMock(),
            ),
            patch(
                "app.services.file_delete.delete",
                new=AsyncMock(),
            ) as delete_mock,
            patch(
                "app.services.file_delete.write_audit",
                new=AsyncMock(),
            ),
            patch(
                "app.services.file_delete.hooks.emit",
                new=AsyncMock(),
            ),
        ):
            result = await delete_file(session=session, file_id=42)

        self.assertIs(result, file)
        repository.commit.assert_awaited_once()
        delete_mock.assert_awaited_once_with(TMP_PATH)
