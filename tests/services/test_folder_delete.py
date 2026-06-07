# tests/services/test_folder_delete.py
# SPDX-License-Identifier: SSPL-1.0

import unittest
from unittest.mock import AsyncMock, MagicMock, call, patch

from app.errors import (
    ResourceConflictError,
    ResourceLockedError,
    ResourceNotFoundError,
)
from app.events import Events as E
from app.locks import LockType
from app.models.file import File
from app.models.folder import Folder
from app.services.folder_delete import delete_folder


class TestDeleteFolder(unittest.IsolatedAsyncioTestCase):

    def _build_lock_context(self):
        lock_context = AsyncMock()
        lock_context.__aenter__.return_value = None
        lock_context.__aexit__.return_value = None
        return lock_context

    def _build_folder(self):
        folder = MagicMock(spec=Folder)
        folder.id = 42
        folder.children_count = 0
        folder.files_count = 0
        folder.is_write_protected = False
        folder.is_write_protected_recursive.return_value = False
        folder.get_absolute_dir.return_value = "/mnt/files/parent/docs"
        return folder

    def _build_parent(self):
        parent = MagicMock(spec=Folder)
        parent.id = 1
        parent.children_count = 2
        parent.get_absolute_dir.return_value = "/mnt/files/parent"
        return parent

    def _build_file(self, file_id):
        file = MagicMock(spec=File)
        file.id = file_id
        return file

    async def test_deletes_files_folder_writes_audit_commits(self):
        session = AsyncMock()

        folder = self._build_folder()
        parent = self._build_parent()
        parent_chain = (parent,)
        files = [self._build_file(100), self._build_file(101)]

        repository = AsyncMock()
        repository.select.side_effect = [folder, folder]
        repository.select_parent_chain.return_value = parent_chain
        repository.select_all.return_value = files

        lock_context = self._build_lock_context()

        with (
            patch(
                "app.services.folder_delete.ORMRepository",
                return_value=repository,
            ),
            patch(
                "app.services.folder_delete.delete_file",
                new=AsyncMock(),
            ) as delete_file_mock,
            patch(
                "app.services.folder_delete.locks.lock_directory",
                return_value=lock_context,
            ) as lock_directory_mock,
            patch(
                "app.services.folder_delete.rmdir",
                new=AsyncMock(),
            ) as rmdir_mock,
            patch(
                "app.services.folder_delete.write_audit",
                new=AsyncMock(),
            ) as write_audit_mock,
            patch(
                "app.services.folder_delete.hooks.emit",
                new=AsyncMock(),
            ) as emit_mock,
        ):
            result = await delete_folder(session=session, folder_id=42)

        self.assertIs(result, folder)

        self.assertEqual(
            repository.select.await_args_list,
            [
                call(Folder, obj_id=42),
                call(Folder, obj_id=42),
            ],
        )
        self.assertEqual(
            repository.select_parent_chain.await_args_list,
            [
                call(folder),
                call(folder),
            ],
        )
        repository.select_all.assert_awaited_once_with(File, folder_id=42)

        self.assertEqual(
            delete_file_mock.await_args_list,
            [
                call(session=session, file_id=100),
                call(session=session, file_id=101),
            ],
        )

        folder.get_absolute_dir.assert_called_once_with(parent_chain)
        parent.get_absolute_dir.assert_called_once_with(())

        lock_directory_mock.assert_called_once_with(
            "/mnt/files/parent",
            LockType.WRITE,
        )
        lock_context.__aenter__.assert_awaited_once()
        lock_context.__aexit__.assert_awaited_once()

        rmdir_mock.assert_awaited_once_with("/mnt/files/parent/docs")
        repository.delete.assert_awaited_once_with(folder)

        self.assertEqual(parent.children_count, 1)
        repository.update.assert_awaited_once_with(parent)

        write_audit_mock.assert_awaited_once_with(
            repository=repository,
            event=E.FOLDER_DELETE_COMPLETED,
            resource_type=Folder.__tablename__,
            resource_id=42,
        )
        repository.commit.assert_awaited_once()
        repository.rollback.assert_not_awaited()

        emit_mock.assert_awaited_once_with(
            E.FOLDER_DELETE_COMPLETED,
            session,
            folder,
        )

    async def test_raises_not_found_when_folder_missing(self):
        session = AsyncMock()

        repository = AsyncMock()
        repository.select.return_value = None

        with (
            patch(
                "app.services.folder_delete.ORMRepository",
                return_value=repository,
            ),
            patch(
                "app.services.folder_delete.delete_file",
                new=AsyncMock(),
            ) as delete_file_mock,
            patch(
                "app.services.folder_delete.locks.lock_directory",
            ) as lock_directory_mock,
            patch(
                "app.services.folder_delete.rmdir",
                new=AsyncMock(),
            ) as rmdir_mock,
            patch(
                "app.services.folder_delete.write_audit",
                new=AsyncMock(),
            ) as write_audit_mock,
            patch(
                "app.services.folder_delete.hooks.emit",
                new=AsyncMock(),
            ) as emit_mock,
        ):
            with self.assertRaises(ResourceNotFoundError):
                await delete_folder(session=session, folder_id=42)

        repository.select.assert_awaited_once_with(Folder, obj_id=42)
        repository.select_parent_chain.assert_not_awaited()
        repository.select_all.assert_not_awaited()
        repository.delete.assert_not_awaited()
        repository.update.assert_not_awaited()
        repository.commit.assert_not_awaited()
        repository.rollback.assert_not_awaited()

        delete_file_mock.assert_not_awaited()
        lock_directory_mock.assert_not_called()
        rmdir_mock.assert_not_awaited()
        write_audit_mock.assert_not_awaited()
        emit_mock.assert_not_awaited()

    async def test_raises_locked_when_folder_protected(self):
        session = AsyncMock()

        folder = self._build_folder()
        folder.is_write_protected_recursive.return_value = True
        parent_chain = (MagicMock(),)

        repository = AsyncMock()
        repository.select.return_value = folder
        repository.select_parent_chain.return_value = parent_chain

        with (
            patch(
                "app.services.folder_delete.ORMRepository",
                return_value=repository,
            ),
            patch(
                "app.services.folder_delete.delete_file",
                new=AsyncMock(),
            ) as delete_file_mock,
            patch(
                "app.services.folder_delete.locks.lock_directory",
            ) as lock_directory_mock,
            patch(
                "app.services.folder_delete.rmdir",
                new=AsyncMock(),
            ) as rmdir_mock,
            patch(
                "app.services.folder_delete.write_audit",
                new=AsyncMock(),
            ) as write_audit_mock,
            patch(
                "app.services.folder_delete.hooks.emit",
                new=AsyncMock(),
            ) as emit_mock,
        ):
            with self.assertRaises(ResourceLockedError):
                await delete_folder(session=session, folder_id=42)

        repository.select.assert_awaited_once_with(Folder, obj_id=42)
        repository.select_parent_chain.assert_awaited_once_with(folder)
        folder.is_write_protected_recursive.assert_called_once_with(
            parent_chain,
        )

        repository.select_all.assert_not_awaited()
        repository.delete.assert_not_awaited()
        repository.update.assert_not_awaited()
        repository.commit.assert_not_awaited()
        repository.rollback.assert_not_awaited()

        delete_file_mock.assert_not_awaited()
        lock_directory_mock.assert_not_called()
        rmdir_mock.assert_not_awaited()
        write_audit_mock.assert_not_awaited()
        emit_mock.assert_not_awaited()

    async def test_raises_conflict_when_folder_has_folders(self):
        session = AsyncMock()

        folder = self._build_folder()
        folder.children_count = 1
        parent_chain = (MagicMock(),)

        repository = AsyncMock()
        repository.select.return_value = folder
        repository.select_parent_chain.return_value = parent_chain

        with (
            patch(
                "app.services.folder_delete.ORMRepository",
                return_value=repository,
            ),
            patch(
                "app.services.folder_delete.delete_file",
                new=AsyncMock(),
            ) as delete_file_mock,
            patch(
                "app.services.folder_delete.locks.lock_directory",
            ) as lock_directory_mock,
            patch(
                "app.services.folder_delete.rmdir",
                new=AsyncMock(),
            ) as rmdir_mock,
            patch(
                "app.services.folder_delete.write_audit",
                new=AsyncMock(),
            ) as write_audit_mock,
            patch(
                "app.services.folder_delete.hooks.emit",
                new=AsyncMock(),
            ) as emit_mock,
        ):
            with self.assertRaises(ResourceConflictError):
                await delete_folder(session=session, folder_id=42)

        repository.select.assert_awaited_once_with(Folder, obj_id=42)
        repository.select_parent_chain.assert_awaited_once_with(folder)
        repository.select_all.assert_not_awaited()
        repository.delete.assert_not_awaited()
        repository.update.assert_not_awaited()
        repository.commit.assert_not_awaited()
        repository.rollback.assert_not_awaited()

        delete_file_mock.assert_not_awaited()
        lock_directory_mock.assert_not_called()
        rmdir_mock.assert_not_awaited()
        write_audit_mock.assert_not_awaited()
        emit_mock.assert_not_awaited()

    async def test_stops_without_folder_delete_when_file_delete_fails(self):
        session = AsyncMock()

        folder = self._build_folder()
        files = [self._build_file(100), self._build_file(101)]

        repository = AsyncMock()
        repository.select.return_value = folder
        repository.select_parent_chain.return_value = ()
        repository.select_all.return_value = files

        error = RuntimeError("file delete failed")

        with (
            patch(
                "app.services.folder_delete.ORMRepository",
                return_value=repository,
            ),
            patch(
                "app.services.folder_delete.delete_file",
                new=AsyncMock(side_effect=error),
            ) as delete_file_mock,
            patch(
                "app.services.folder_delete.locks.lock_directory",
            ) as lock_directory_mock,
            patch(
                "app.services.folder_delete.rmdir",
                new=AsyncMock(),
            ) as rmdir_mock,
            patch(
                "app.services.folder_delete.write_audit",
                new=AsyncMock(),
            ) as write_audit_mock,
            patch(
                "app.services.folder_delete.hooks.emit",
                new=AsyncMock(),
            ) as emit_mock,
        ):
            with self.assertRaises(RuntimeError):
                await delete_folder(session=session, folder_id=42)

        delete_file_mock.assert_awaited_once_with(
            session=session,
            file_id=100,
        )

        repository.delete.assert_not_awaited()
        repository.update.assert_not_awaited()
        repository.commit.assert_not_awaited()
        repository.rollback.assert_not_awaited()

        lock_directory_mock.assert_not_called()
        rmdir_mock.assert_not_awaited()
        write_audit_mock.assert_not_awaited()
        emit_mock.assert_not_awaited()

    async def test_not_found_after_file_deletion_without_folder(self):
        session = AsyncMock()

        folder = self._build_folder()
        files = [self._build_file(100)]

        repository = AsyncMock()
        repository.select.side_effect = [folder, None]
        repository.select_parent_chain.return_value = ()
        repository.select_all.return_value = files

        with (
            patch(
                "app.services.folder_delete.ORMRepository",
                return_value=repository,
            ),
            patch(
                "app.services.folder_delete.delete_file",
                new=AsyncMock(),
            ) as delete_file_mock,
            patch(
                "app.services.folder_delete.locks.lock_directory",
            ) as lock_directory_mock,
            patch(
                "app.services.folder_delete.rmdir",
                new=AsyncMock(),
            ) as rmdir_mock,
            patch(
                "app.services.folder_delete.write_audit",
                new=AsyncMock(),
            ) as write_audit_mock,
            patch(
                "app.services.folder_delete.hooks.emit",
                new=AsyncMock(),
            ) as emit_mock,
        ):
            with self.assertRaises(ResourceNotFoundError):
                await delete_folder(session=session, folder_id=42)

        delete_file_mock.assert_awaited_once_with(
            session=session,
            file_id=100,
        )

        repository.delete.assert_not_awaited()
        repository.update.assert_not_awaited()
        repository.commit.assert_not_awaited()
        repository.rollback.assert_not_awaited()

        lock_directory_mock.assert_not_called()
        rmdir_mock.assert_not_awaited()
        write_audit_mock.assert_not_awaited()
        emit_mock.assert_not_awaited()

    async def test_raises_conflict_after_file_deletion_when_files_remain(self):
        session = AsyncMock()

        folder = self._build_folder()
        folder_after_files = self._build_folder()
        folder_after_files.files_count = 1

        files = [self._build_file(100)]

        repository = AsyncMock()
        repository.select.side_effect = [folder, folder_after_files]
        repository.select_parent_chain.return_value = ()
        repository.select_all.return_value = files

        with (
            patch(
                "app.services.folder_delete.ORMRepository",
                return_value=repository,
            ),
            patch(
                "app.services.folder_delete.delete_file",
                new=AsyncMock(),
            ) as delete_file_mock,
            patch(
                "app.services.folder_delete.locks.lock_directory",
            ) as lock_directory_mock,
            patch(
                "app.services.folder_delete.rmdir",
                new=AsyncMock(),
            ) as rmdir_mock,
            patch(
                "app.services.folder_delete.write_audit",
                new=AsyncMock(),
            ) as write_audit_mock,
            patch(
                "app.services.folder_delete.hooks.emit",
                new=AsyncMock(),
            ) as emit_mock,
        ):
            with self.assertRaises(ResourceConflictError):
                await delete_folder(session=session, folder_id=42)

        delete_file_mock.assert_awaited_once_with(
            session=session,
            file_id=100,
        )

        repository.delete.assert_not_awaited()
        repository.update.assert_not_awaited()
        repository.commit.assert_not_awaited()
        repository.rollback.assert_not_awaited()

        lock_directory_mock.assert_not_called()
        rmdir_mock.assert_not_awaited()
        write_audit_mock.assert_not_awaited()
        emit_mock.assert_not_awaited()

    async def test_rolls_back_when_rmdir_fails(self):
        session = AsyncMock()

        folder = self._build_folder()
        parent = self._build_parent()
        parent_chain = (parent,)

        repository = AsyncMock()
        repository.select.side_effect = [folder, folder]
        repository.select_parent_chain.return_value = parent_chain
        repository.select_all.return_value = []

        lock_context = self._build_lock_context()
        error = RuntimeError("rmdir failed")

        with (
            patch(
                "app.services.folder_delete.ORMRepository",
                return_value=repository,
            ),
            patch(
                "app.services.folder_delete.delete_file",
                new=AsyncMock(),
            ) as delete_file_mock,
            patch(
                "app.services.folder_delete.locks.lock_directory",
                return_value=lock_context,
            ) as lock_directory_mock,
            patch(
                "app.services.folder_delete.rmdir",
                new=AsyncMock(side_effect=error),
            ) as rmdir_mock,
            patch(
                "app.services.folder_delete.write_audit",
                new=AsyncMock(),
            ) as write_audit_mock,
            patch(
                "app.services.folder_delete.hooks.emit",
                new=AsyncMock(),
            ) as emit_mock,
        ):
            with self.assertRaises(RuntimeError):
                await delete_folder(session=session, folder_id=42)

        delete_file_mock.assert_not_awaited()

        lock_directory_mock.assert_called_once_with(
            "/mnt/files/parent",
            LockType.WRITE,
        )
        rmdir_mock.assert_awaited_once_with("/mnt/files/parent/docs")

        repository.rollback.assert_awaited_once()
        repository.delete.assert_not_awaited()
        repository.update.assert_not_awaited()
        repository.commit.assert_not_awaited()

        write_audit_mock.assert_not_awaited()
        emit_mock.assert_not_awaited()

    async def test_logs_inconsistent_rollback_db_step_fails_after_rmdir(self):
        session = AsyncMock()

        folder = self._build_folder()
        parent = self._build_parent()
        parent_chain = (parent,)

        repository = AsyncMock()
        repository.select.side_effect = [folder, folder]
        repository.select_parent_chain.return_value = parent_chain
        repository.select_all.return_value = []
        repository.delete.side_effect = RuntimeError("delete failed")

        lock_context = self._build_lock_context()

        with (
            patch(
                "app.services.folder_delete.ORMRepository",
                return_value=repository,
            ),
            patch(
                "app.services.folder_delete.delete_file",
                new=AsyncMock(),
            ) as delete_file_mock,
            patch(
                "app.services.folder_delete.locks.lock_directory",
                return_value=lock_context,
            ),
            patch(
                "app.services.folder_delete.rmdir",
                new=AsyncMock(),
            ) as rmdir_mock,
            patch(
                "app.services.folder_delete.write_audit",
                new=AsyncMock(),
            ) as write_audit_mock,
            patch(
                "app.services.folder_delete.hooks.emit",
                new=AsyncMock(),
            ) as emit_mock,
            patch(
                "app.services.folder_delete.log.exception",
            ) as log_exception_mock,
        ):
            with self.assertRaises(RuntimeError):
                await delete_folder(session=session, folder_id=42)

        delete_file_mock.assert_not_awaited()
        rmdir_mock.assert_awaited_once_with("/mnt/files/parent/docs")
        repository.delete.assert_awaited_once_with(folder)
        repository.rollback.assert_awaited_once()
        repository.commit.assert_not_awaited()

        write_audit_mock.assert_not_awaited()
        emit_mock.assert_not_awaited()

        log_exception_mock.assert_called_once_with(
            "event=%s",
            E.FOLDER_DELETE_INCONSISTENT,
        )

    async def test_raises_locked_after_files_when_reloaded_folder_protected(
        self,
    ):
        """Second-phase check (lines 78–82) after delete_file loop."""
        session = AsyncMock()

        folder_before = self._build_folder()
        folder_after = self._build_folder()
        folder_after.is_write_protected_recursive.return_value = True
        files = [self._build_file(100)]
        parent_chain = (MagicMock(),)

        repository = AsyncMock()
        repository.select.side_effect = [folder_before, folder_after]
        repository.select_parent_chain.return_value = parent_chain
        repository.select_all.return_value = files

        with (
            patch(
                "app.services.folder_delete.ORMRepository",
                return_value=repository,
            ),
            patch(
                "app.services.folder_delete.delete_file",
                new=AsyncMock(),
            ) as delete_file_mock,
            patch(
                "app.services.folder_delete.locks.lock_directory",
            ) as lock_directory_mock,
            patch(
                "app.services.folder_delete.rmdir",
                new=AsyncMock(),
            ),
            patch(
                "app.services.folder_delete.write_audit",
                new=AsyncMock(),
            ),
            patch(
                "app.services.folder_delete.hooks.emit",
                new=AsyncMock(),
            ),
        ):
            with self.assertRaises(ResourceLockedError):
                await delete_folder(session=session, folder_id=42)

        delete_file_mock.assert_awaited_once_with(
            session=session,
            file_id=100,
        )
        folder_after.is_write_protected_recursive.assert_called_with(
            parent_chain,
        )
        lock_directory_mock.assert_not_called()

    async def test_raises_conflict_after_files_reloaded_folder_has_children(
        self,
    ):
        """Second-phase children_count check (lines 84–86)."""
        session = AsyncMock()

        folder_before = self._build_folder()
        folder_after = self._build_folder()
        folder_after.children_count = 1
        files = [self._build_file(100)]
        parent_chain = (MagicMock(),)

        repository = AsyncMock()
        repository.select.side_effect = [folder_before, folder_after]
        repository.select_parent_chain.return_value = parent_chain
        repository.select_all.return_value = files

        with (
            patch(
                "app.services.folder_delete.ORMRepository",
                return_value=repository,
            ),
            patch(
                "app.services.folder_delete.delete_file",
                new=AsyncMock(),
            ) as delete_file_mock,
            patch(
                "app.services.folder_delete.locks.lock_directory",
            ) as lock_directory_mock,
            patch(
                "app.services.folder_delete.rmdir",
                new=AsyncMock(),
            ),
            patch(
                "app.services.folder_delete.write_audit",
                new=AsyncMock(),
            ),
            patch(
                "app.services.folder_delete.hooks.emit",
                new=AsyncMock(),
            ),
        ):
            with self.assertRaises(ResourceConflictError):
                await delete_folder(session=session, folder_id=42)

        delete_file_mock.assert_awaited_once_with(
            session=session,
            file_id=100,
        )
        lock_directory_mock.assert_not_called()

    async def test_locks_target_folder_path_when_no_parent(self):
        """Root folder: lock_dir == absolute_dir (line 98)."""
        session = AsyncMock()

        folder = self._build_folder()
        folder.get_absolute_dir.return_value = "/mnt/files/root-only"

        repository = AsyncMock()
        repository.select.side_effect = [folder, folder]
        repository.select_parent_chain.return_value = ()
        repository.select_all.return_value = []

        lock_context = self._build_lock_context()

        with (
            patch(
                "app.services.folder_delete.ORMRepository",
                return_value=repository,
            ),
            patch(
                "app.services.folder_delete.delete_file",
                new=AsyncMock(),
            ),
            patch(
                "app.services.folder_delete.locks.lock_directory",
                return_value=lock_context,
            ) as lock_directory_mock,
            patch(
                "app.services.folder_delete.rmdir",
                new=AsyncMock(),
            ) as rmdir_mock,
            patch(
                "app.services.folder_delete.write_audit",
                new=AsyncMock(),
            ),
            patch(
                "app.services.folder_delete.hooks.emit",
                new=AsyncMock(),
            ),
        ):
            await delete_folder(session=session, folder_id=42)

        lock_directory_mock.assert_called_once_with(
            "/mnt/files/root-only",
            LockType.WRITE,
        )
        rmdir_mock.assert_awaited_once_with("/mnt/files/root-only")
        folder.get_absolute_dir.assert_called_once_with(())
        repository.update.assert_not_awaited()
