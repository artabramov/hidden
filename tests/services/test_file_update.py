# tests/services/test_file_update.py
# SPDX-License-Identifier: GPL-3.0-only

import unittest
from unittest.mock import AsyncMock, MagicMock, call, patch

from sqlalchemy.exc import IntegrityError

from app.constants import FILES_MAX_PATH_LENGTH_BYTES
from app.errors import (
    ResourceConflictError,
    ResourceLockedError,
    ResourceNotFoundError,
)
from app.events import Events as E
from app.locks import LockType
from app.models.file import File
from app.models.folder import Folder
from app.models.user import User
from app.services.file_update import update_file


class TestUpdateFile(unittest.IsolatedAsyncioTestCase):

    def _build_user(self):
        user = MagicMock(spec=User)
        user.id = 10
        return user

    def _build_data(self):
        data = MagicMock()
        data.filename = "new-document.txt"
        data.summary = "New file summary"
        data.model_fields_set = {"filename", "summary"}
        return data

    def _build_lock_context(self):
        lock_context = AsyncMock()
        lock_context.__aenter__.return_value = None
        lock_context.__aexit__.return_value = None
        return lock_context

    def _build_folder(self):
        folder = MagicMock(spec=Folder)
        folder.id = 2
        folder.is_write_protected = False
        folder.is_write_protected_recursive.return_value = False
        folder.get_absolute_dir.return_value = "/mnt/files/folder"
        return folder

    def _build_file(self, folder):
        file = MagicMock(spec=File)
        file.id = 42
        file.filename = "document.txt"
        file.summary = "Old file summary"
        file.updated_by = None
        file.file_folder = folder
        file.get_absolute_path.side_effect = [
            "/mnt/files/folder/document.txt",
            "/mnt/files/folder/new-document.txt",
        ]
        return file

    async def test_updates_file_renames_path_commits_and_emits_hook(
        self,
    ):
        session = AsyncMock()
        user = self._build_user()
        data = self._build_data()

        folder = self._build_folder()
        file = self._build_file(folder)
        parent_chain = (MagicMock(),)

        repository = AsyncMock()
        repository.select.return_value = file
        repository.select_parent_chain.return_value = parent_chain

        lock_context = self._build_lock_context()

        with (
            patch(
                "app.services.file_update.ORMRepository",
                return_value=repository,
            ),
            patch(
                "app.services.file_update.locks.lock_directory",
                return_value=lock_context,
            ) as lock_directory_mock,
            patch(
                "app.services.file_update.rename",
                new=AsyncMock(),
            ) as rename_mock,
            patch(
                "app.services.file_update.isdir",
                new=AsyncMock(return_value=False),
            ) as isdir_mock,
            patch(
                "app.services.file_update.isfile",
                new=AsyncMock(return_value=False),
            ) as isfile_mock,
            patch(
                "app.services.file_update.write_audit",
                new=AsyncMock(),
            ) as write_audit_mock,
            patch(
                "app.services.file_update.hooks.emit",
                new=AsyncMock(),
            ) as emit_mock,
        ):
            result = await update_file(session, user, 42, data)

        self.assertIs(result, file)
        self.assertEqual(file.filename, "new-document.txt")
        self.assertEqual(file.summary, "New file summary")
        self.assertEqual(file.updated_by, 10)

        repository.select.assert_awaited_once_with(File, obj_id=42)
        repository.select_parent_chain.assert_awaited_once_with(folder)
        folder.is_write_protected_recursive.assert_called_once_with(
            parent_chain,
        )

        self.assertEqual(
            file.get_absolute_path.call_args_list,
            [
                call(folder, parent_chain),
                call(folder, parent_chain),
            ],
        )
        folder.get_absolute_dir.assert_called_once_with(parent_chain)

        lock_directory_mock.assert_called_once_with(
            "/mnt/files/folder",
            LockType.WRITE,
        )
        lock_context.__aenter__.assert_awaited_once()
        lock_context.__aexit__.assert_awaited_once()

        isdir_mock.assert_awaited_once_with(
            "/mnt/files/folder/new-document.txt",
        )
        isfile_mock.assert_awaited_once_with(
            "/mnt/files/folder/new-document.txt",
        )
        rename_mock.assert_awaited_once_with(
            "/mnt/files/folder/document.txt",
            "/mnt/files/folder/new-document.txt",
        )

        repository.update.assert_awaited_once_with(file)

        write_audit_mock.assert_awaited_once_with(
            repository=repository,
            event=E.FILE_UPDATE_COMPLETED,
            resource_type=File.__tablename__,
            resource_id=42,
        )
        repository.commit.assert_awaited_once()
        repository.rollback.assert_not_awaited()

        emit_mock.assert_awaited_once_with(
            E.FILE_UPDATE_COMPLETED,
            session,
            file,
        )

    async def test_raises_not_found(self):
        session = AsyncMock()
        user = self._build_user()
        data = self._build_data()

        repository = AsyncMock()
        repository.select.return_value = None

        with (
            patch(
                "app.services.file_update.ORMRepository",
                return_value=repository,
            ),
            patch(
                "app.services.file_update.locks.lock_directory",
            ) as lock_directory_mock,
            patch(
                "app.services.file_update.rename",
                new=AsyncMock(),
            ) as rename_mock,
            patch(
                "app.services.file_update.write_audit",
                new=AsyncMock(),
            ) as write_audit_mock,
            patch(
                "app.services.file_update.hooks.emit",
                new=AsyncMock(),
            ) as emit_mock,
            patch(
                "app.services.file_update.isdir",
                new=AsyncMock(),
            ) as isdir_mock,
            patch(
                "app.services.file_update.isfile",
                new=AsyncMock(),
            ) as isfile_mock,
        ):
            with self.assertRaises(ResourceNotFoundError):
                await update_file(session, user, 42, data)

        repository.select.assert_awaited_once_with(File, obj_id=42)
        repository.select_parent_chain.assert_not_awaited()
        repository.update.assert_not_awaited()
        repository.commit.assert_not_awaited()
        repository.rollback.assert_not_awaited()

        lock_directory_mock.assert_not_called()
        rename_mock.assert_not_awaited()
        write_audit_mock.assert_not_awaited()
        emit_mock.assert_not_awaited()
        isdir_mock.assert_not_awaited()
        isfile_mock.assert_not_awaited()

    async def test_raises_locked_when_parent_folder_write_protected(self):
        session = AsyncMock()
        user = self._build_user()
        data = self._build_data()

        folder = self._build_folder()
        folder.is_write_protected_recursive.return_value = True
        file = self._build_file(folder)
        parent_chain = (MagicMock(),)

        repository = AsyncMock()
        repository.select.return_value = file
        repository.select_parent_chain.return_value = parent_chain

        with (
            patch(
                "app.services.file_update.ORMRepository",
                return_value=repository,
            ),
            patch(
                "app.services.file_update.locks.lock_directory",
            ) as lock_directory_mock,
            patch(
                "app.services.file_update.rename",
                new=AsyncMock(),
            ) as rename_mock,
            patch(
                "app.services.file_update.write_audit",
                new=AsyncMock(),
            ) as write_audit_mock,
            patch(
                "app.services.file_update.hooks.emit",
                new=AsyncMock(),
            ) as emit_mock,
            patch(
                "app.services.file_update.isdir",
                new=AsyncMock(),
            ) as isdir_mock,
            patch(
                "app.services.file_update.isfile",
                new=AsyncMock(),
            ) as isfile_mock,
        ):
            with self.assertRaises(ResourceLockedError):
                await update_file(session, user, 42, data)

        repository.select.assert_awaited_once_with(File, obj_id=42)
        repository.select_parent_chain.assert_awaited_once_with(folder)
        folder.is_write_protected_recursive.assert_called_once_with(
            parent_chain,
        )

        repository.update.assert_not_awaited()
        repository.commit.assert_not_awaited()
        repository.rollback.assert_not_awaited()

        lock_directory_mock.assert_not_called()
        rename_mock.assert_not_awaited()
        write_audit_mock.assert_not_awaited()
        emit_mock.assert_not_awaited()
        isdir_mock.assert_not_awaited()
        isfile_mock.assert_not_awaited()

    async def test_preserves_summary_when_summary_not_provided(self):
        session = AsyncMock()
        user = self._build_user()
        data = self._build_data()
        data.summary = "Ignored summary"
        data.model_fields_set = {"filename"}

        folder = self._build_folder()
        file = self._build_file(folder)
        parent_chain = ()

        repository = AsyncMock()
        repository.select.return_value = file
        repository.select_parent_chain.return_value = parent_chain

        lock_context = self._build_lock_context()

        with (
            patch(
                "app.services.file_update.ORMRepository",
                return_value=repository,
            ),
            patch(
                "app.services.file_update.locks.lock_directory",
                return_value=lock_context,
            ),
            patch(
                "app.services.file_update.rename",
                new=AsyncMock(),
            ),
            patch(
                "app.services.file_update.isdir",
                new=AsyncMock(return_value=False),
            ),
            patch(
                "app.services.file_update.isfile",
                new=AsyncMock(return_value=False),
            ),
            patch(
                "app.services.file_update.write_audit",
                new=AsyncMock(),
            ),
            patch(
                "app.services.file_update.hooks.emit",
                new=AsyncMock(),
            ),
        ):
            await update_file(session, user, 42, data)

        self.assertEqual(file.filename, "new-document.txt")
        self.assertEqual(file.summary, "Old file summary")

    async def test_clears_summary_when_summary_provided_as_none(self):
        session = AsyncMock()
        user = self._build_user()
        data = self._build_data()
        data.summary = None
        data.model_fields_set = {"filename", "summary"}

        folder = self._build_folder()
        file = self._build_file(folder)
        parent_chain = ()

        repository = AsyncMock()
        repository.select.return_value = file
        repository.select_parent_chain.return_value = parent_chain

        lock_context = self._build_lock_context()

        with (
            patch(
                "app.services.file_update.ORMRepository",
                return_value=repository,
            ),
            patch(
                "app.services.file_update.locks.lock_directory",
                return_value=lock_context,
            ),
            patch(
                "app.services.file_update.rename",
                new=AsyncMock(),
            ),
            patch(
                "app.services.file_update.isdir",
                new=AsyncMock(return_value=False),
            ),
            patch(
                "app.services.file_update.isfile",
                new=AsyncMock(return_value=False),
            ),
            patch(
                "app.services.file_update.write_audit",
                new=AsyncMock(),
            ),
            patch(
                "app.services.file_update.hooks.emit",
                new=AsyncMock(),
            ),
        ):
            await update_file(session, user, 42, data)

        self.assertIsNone(file.summary)

    async def test_does_not_rename_when_filename_unchanged(self):
        session = AsyncMock()
        user = self._build_user()
        data = self._build_data()
        data.filename = "document.txt"

        folder = self._build_folder()
        file = self._build_file(folder)
        file.get_absolute_path.side_effect = [
            "/mnt/files/folder/document.txt",
            "/mnt/files/folder/document.txt",
        ]
        parent_chain = ()

        repository = AsyncMock()
        repository.select.return_value = file
        repository.select_parent_chain.return_value = parent_chain

        lock_context = self._build_lock_context()

        with (
            patch(
                "app.services.file_update.ORMRepository",
                return_value=repository,
            ),
            patch(
                "app.services.file_update.locks.lock_directory",
                return_value=lock_context,
            ),
            patch(
                "app.services.file_update.rename",
                new=AsyncMock(),
            ) as rename_mock,
            patch(
                "app.services.file_update.isdir",
                new=AsyncMock(),
            ) as isdir_mock,
            patch(
                "app.services.file_update.isfile",
                new=AsyncMock(),
            ) as isfile_mock,
            patch(
                "app.services.file_update.write_audit",
                new=AsyncMock(),
            ) as write_audit_mock,
            patch(
                "app.services.file_update.hooks.emit",
                new=AsyncMock(),
            ) as emit_mock,
        ):
            await update_file(session, user, 42, data)

        repository.update.assert_awaited_once_with(file)
        rename_mock.assert_not_awaited()
        isdir_mock.assert_not_awaited()
        isfile_mock.assert_not_awaited()
        write_audit_mock.assert_awaited_once()
        repository.commit.assert_awaited_once()
        emit_mock.assert_awaited_once()

    async def test_raises_conflict_when_new_path_is_directory(
        self,
    ):
        session = AsyncMock()
        user = self._build_user()
        data = self._build_data()

        folder = self._build_folder()
        file = self._build_file(folder)
        parent_chain = ()

        repository = AsyncMock()
        repository.select.return_value = file
        repository.select_parent_chain.return_value = parent_chain

        lock_context = self._build_lock_context()

        with (
            patch(
                "app.services.file_update.ORMRepository",
                return_value=repository,
            ),
            patch(
                "app.services.file_update.locks.lock_directory",
                return_value=lock_context,
            ),
            patch(
                "app.services.file_update.rename",
                new=AsyncMock(),
            ) as rename_mock,
            patch(
                "app.services.file_update.isdir",
                new=AsyncMock(return_value=True),
            ) as isdir_mock,
            patch(
                "app.services.file_update.isfile",
                new=AsyncMock(),
            ) as isfile_mock,
            patch(
                "app.services.file_update.write_audit",
                new=AsyncMock(),
            ) as write_audit_mock,
            patch(
                "app.services.file_update.hooks.emit",
                new=AsyncMock(),
            ) as emit_mock,
        ):
            with self.assertRaises(ResourceConflictError):
                await update_file(session, user, 42, data)

        isdir_mock.assert_awaited_once_with(
            "/mnt/files/folder/new-document.txt",
        )
        isfile_mock.assert_not_awaited()
        rename_mock.assert_not_awaited()
        repository.update.assert_not_awaited()
        repository.commit.assert_not_awaited()
        repository.rollback.assert_not_awaited()
        write_audit_mock.assert_not_awaited()
        emit_mock.assert_not_awaited()

    async def test_raises_conflict_when_new_path_is_file(self):
        session = AsyncMock()
        user = self._build_user()
        data = self._build_data()

        folder = self._build_folder()
        file = self._build_file(folder)
        parent_chain = ()

        repository = AsyncMock()
        repository.select.return_value = file
        repository.select_parent_chain.return_value = parent_chain

        lock_context = self._build_lock_context()

        with (
            patch(
                "app.services.file_update.ORMRepository",
                return_value=repository,
            ),
            patch(
                "app.services.file_update.locks.lock_directory",
                return_value=lock_context,
            ),
            patch(
                "app.services.file_update.rename",
                new=AsyncMock(),
            ) as rename_mock,
            patch(
                "app.services.file_update.isdir",
                new=AsyncMock(return_value=False),
            ) as isdir_mock,
            patch(
                "app.services.file_update.isfile",
                new=AsyncMock(return_value=True),
            ) as isfile_mock,
            patch(
                "app.services.file_update.write_audit",
                new=AsyncMock(),
            ) as write_audit_mock,
            patch(
                "app.services.file_update.hooks.emit",
                new=AsyncMock(),
            ) as emit_mock,
        ):
            with self.assertRaises(ResourceConflictError):
                await update_file(session, user, 42, data)

        isdir_mock.assert_awaited_once_with(
            "/mnt/files/folder/new-document.txt",
        )
        isfile_mock.assert_awaited_once_with(
            "/mnt/files/folder/new-document.txt",
        )
        rename_mock.assert_not_awaited()
        repository.update.assert_not_awaited()
        repository.commit.assert_not_awaited()
        repository.rollback.assert_not_awaited()
        write_audit_mock.assert_not_awaited()
        emit_mock.assert_not_awaited()

    async def test_raises_conflict_when_path_too_long(self):
        session = AsyncMock()
        user = self._build_user()
        data = self._build_data()

        folder = self._build_folder()
        file = self._build_file(folder)
        file.get_absolute_path.side_effect = [
            "/mnt/files/folder/document.txt",
            "/" + ("a" * FILES_MAX_PATH_LENGTH_BYTES),
        ]
        parent_chain = ()

        repository = AsyncMock()
        repository.select.return_value = file
        repository.select_parent_chain.return_value = parent_chain

        with (
            patch(
                "app.services.file_update.ORMRepository",
                return_value=repository,
            ),
            patch(
                "app.services.file_update.locks.lock_directory",
            ) as lock_directory_mock,
            patch(
                "app.services.file_update.rename",
                new=AsyncMock(),
            ) as rename_mock,
            patch(
                "app.services.file_update.isdir",
                new=AsyncMock(),
            ) as isdir_mock,
            patch(
                "app.services.file_update.isfile",
                new=AsyncMock(),
            ) as isfile_mock,
            patch(
                "app.services.file_update.write_audit",
                new=AsyncMock(),
            ) as write_audit_mock,
            patch(
                "app.services.file_update.hooks.emit",
                new=AsyncMock(),
            ) as emit_mock,
        ):
            with self.assertRaises(ResourceConflictError):
                await update_file(session, user, 42, data)

        lock_directory_mock.assert_not_called()
        isdir_mock.assert_not_awaited()
        isfile_mock.assert_not_awaited()
        rename_mock.assert_not_awaited()
        repository.update.assert_not_awaited()
        repository.commit.assert_not_awaited()
        repository.rollback.assert_not_awaited()
        write_audit_mock.assert_not_awaited()
        emit_mock.assert_not_awaited()

    async def test_rolls_back_and_raises_conflict_on_update_integrity_error(
        self,
    ):
        session = AsyncMock()
        user = self._build_user()
        data = self._build_data()

        folder = self._build_folder()
        file = self._build_file(folder)
        parent_chain = ()

        repository = AsyncMock()
        repository.select.return_value = file
        repository.select_parent_chain.return_value = parent_chain
        repository.update.side_effect = IntegrityError(None, None, None)

        lock_context = self._build_lock_context()

        with (
            patch(
                "app.services.file_update.ORMRepository",
                return_value=repository,
            ),
            patch(
                "app.services.file_update.locks.lock_directory",
                return_value=lock_context,
            ),
            patch(
                "app.services.file_update.rename",
                new=AsyncMock(),
            ) as rename_mock,
            patch(
                "app.services.file_update.isdir",
                new=AsyncMock(return_value=False),
            ),
            patch(
                "app.services.file_update.isfile",
                new=AsyncMock(return_value=False),
            ),
            patch(
                "app.services.file_update.write_audit",
                new=AsyncMock(),
            ) as write_audit_mock,
            patch(
                "app.services.file_update.hooks.emit",
                new=AsyncMock(),
            ) as emit_mock,
        ):
            with self.assertRaises(ResourceConflictError):
                await update_file(session, user, 42, data)

        repository.update.assert_awaited_once_with(file)
        repository.rollback.assert_awaited_once()
        repository.commit.assert_not_awaited()

        rename_mock.assert_not_awaited()
        write_audit_mock.assert_not_awaited()
        emit_mock.assert_not_awaited()

    async def test_rolls_back_and_restores_file_on_failure_after_rename(self):
        session = AsyncMock()
        user = self._build_user()
        data = self._build_data()

        folder = self._build_folder()
        file = self._build_file(folder)
        parent_chain = ()

        repository = AsyncMock()
        repository.select.return_value = file
        repository.select_parent_chain.return_value = parent_chain

        lock_context = self._build_lock_context()
        error = RuntimeError("audit failed")

        with (
            patch(
                "app.services.file_update.ORMRepository",
                return_value=repository,
            ),
            patch(
                "app.services.file_update.locks.lock_directory",
                return_value=lock_context,
            ),
            patch(
                "app.services.file_update.rename",
                new=AsyncMock(),
            ) as rename_mock,
            patch(
                "app.services.file_update.isdir",
                new=AsyncMock(return_value=False),
            ),
            patch(
                "app.services.file_update.isfile",
                new=AsyncMock(return_value=False),
            ),
            patch(
                "app.services.file_update.write_audit",
                new=AsyncMock(side_effect=error),
            ),
            patch(
                "app.services.file_update.hooks.emit",
                new=AsyncMock(),
            ) as emit_mock,
        ):
            with self.assertRaises(RuntimeError):
                await update_file(session, user, 42, data)

        self.assertEqual(
            rename_mock.await_args_list,
            [
                call(
                    "/mnt/files/folder/document.txt",
                    "/mnt/files/folder/new-document.txt",
                ),
                call(
                    "/mnt/files/folder/new-document.txt",
                    "/mnt/files/folder/document.txt",
                ),
            ],
        )
        repository.rollback.assert_awaited_once()
        repository.commit.assert_not_awaited()
        emit_mock.assert_not_awaited()

    async def test_rolls_back_without_restore_when_update_fails_before_rename(
        self,
    ):
        session = AsyncMock()
        user = self._build_user()
        data = self._build_data()

        folder = self._build_folder()
        file = self._build_file(folder)
        parent_chain = ()

        repository = AsyncMock()
        repository.select.return_value = file
        repository.select_parent_chain.return_value = parent_chain
        repository.update.side_effect = RuntimeError("update failed")

        lock_context = self._build_lock_context()

        with (
            patch(
                "app.services.file_update.ORMRepository",
                return_value=repository,
            ),
            patch(
                "app.services.file_update.locks.lock_directory",
                return_value=lock_context,
            ),
            patch(
                "app.services.file_update.rename",
                new=AsyncMock(),
            ) as rename_mock,
            patch(
                "app.services.file_update.isdir",
                new=AsyncMock(return_value=False),
            ),
            patch(
                "app.services.file_update.isfile",
                new=AsyncMock(return_value=False),
            ),
            patch(
                "app.services.file_update.write_audit",
                new=AsyncMock(),
            ) as write_audit_mock,
            patch(
                "app.services.file_update.hooks.emit",
                new=AsyncMock(),
            ) as emit_mock,
        ):
            with self.assertRaises(RuntimeError):
                await update_file(session, user, 42, data)

        repository.rollback.assert_awaited_once()
        repository.commit.assert_not_awaited()
        rename_mock.assert_not_awaited()
        write_audit_mock.assert_not_awaited()
        emit_mock.assert_not_awaited()

    async def test_restore_failed_rename_back_fails_after_integrity_error(
        self,
    ):
        session = AsyncMock()
        user = self._build_user()
        data = self._build_data()

        folder = self._build_folder()
        file = self._build_file(folder)
        parent_chain = ()

        repository = AsyncMock()
        repository.select.return_value = file
        repository.select_parent_chain.return_value = parent_chain
        repository.commit.side_effect = IntegrityError(
            "stmt",
            "params",
            object(),
        )

        lock_context = self._build_lock_context()

        rename_calls = []

        async def rename_side_effect(old, new):
            rename_calls.append((old, new))
            if len(rename_calls) == 2:
                raise OSError("restore rename failed")

        with (
            patch(
                "app.services.file_update.ORMRepository",
                return_value=repository,
            ),
            patch(
                "app.services.file_update.locks.lock_directory",
                return_value=lock_context,
            ),
            patch(
                "app.services.file_update.rename",
                new=AsyncMock(side_effect=rename_side_effect),
            ) as rename_mock,
            patch(
                "app.services.file_update.isdir",
                new=AsyncMock(return_value=False),
            ),
            patch(
                "app.services.file_update.isfile",
                new=AsyncMock(return_value=False),
            ),
            patch(
                "app.services.file_update.write_audit",
                new=AsyncMock(),
            ),
            patch(
                "app.services.file_update.hooks.emit",
                new=AsyncMock(),
            ) as emit_mock,
            patch(
                "app.services.file_update.log",
                MagicMock(),
            ) as log_mock,
        ):
            with self.assertRaises(ResourceConflictError):
                await update_file(session, user, 42, data)

        self.assertEqual(
            rename_mock.await_args_list,
            [
                call(
                    "/mnt/files/folder/document.txt",
                    "/mnt/files/folder/new-document.txt",
                ),
                call(
                    "/mnt/files/folder/new-document.txt",
                    "/mnt/files/folder/document.txt",
                ),
            ],
        )
        repository.rollback.assert_awaited_once()
        repository.commit.assert_awaited_once()
        emit_mock.assert_not_awaited()
        log_mock.exception.assert_called_once()
        self.assertIn(
            E.FILE_UPDATE_RESTORE_FAILED,
            log_mock.exception.call_args[0],
        )

    async def test_restore_failed_rename_back_fails_after_write_audit_error(
        self,
    ):
        session = AsyncMock()
        user = self._build_user()
        data = self._build_data()

        folder = self._build_folder()
        file = self._build_file(folder)
        parent_chain = ()

        repository = AsyncMock()
        repository.select.return_value = file
        repository.select_parent_chain.return_value = parent_chain

        lock_context = self._build_lock_context()

        rename_calls = []

        async def rename_side_effect(old, new):
            rename_calls.append((old, new))
            if len(rename_calls) == 2:
                raise OSError("restore rename failed")

        with (
            patch(
                "app.services.file_update.ORMRepository",
                return_value=repository,
            ),
            patch(
                "app.services.file_update.locks.lock_directory",
                return_value=lock_context,
            ),
            patch(
                "app.services.file_update.rename",
                new=AsyncMock(side_effect=rename_side_effect),
            ) as rename_mock,
            patch(
                "app.services.file_update.isdir",
                new=AsyncMock(return_value=False),
            ),
            patch(
                "app.services.file_update.isfile",
                new=AsyncMock(return_value=False),
            ),
            patch(
                "app.services.file_update.write_audit",
                new=AsyncMock(side_effect=RuntimeError("audit failed")),
            ),
            patch(
                "app.services.file_update.hooks.emit",
                new=AsyncMock(),
            ) as emit_mock,
            patch(
                "app.services.file_update.log",
                MagicMock(),
            ) as log_mock,
        ):
            with self.assertRaises(RuntimeError):
                await update_file(session, user, 42, data)

        self.assertEqual(
            rename_mock.await_args_list,
            [
                call(
                    "/mnt/files/folder/document.txt",
                    "/mnt/files/folder/new-document.txt",
                ),
                call(
                    "/mnt/files/folder/new-document.txt",
                    "/mnt/files/folder/document.txt",
                ),
            ],
        )
        repository.rollback.assert_awaited_once()
        emit_mock.assert_not_awaited()
        log_mock.exception.assert_called_once()
        self.assertIn(
            E.FILE_UPDATE_RESTORE_FAILED,
            log_mock.exception.call_args[0],
        )
